package harbor.service

import harbor.dao.ParameterDao
import harbor.enums.ParameterKey
import harbor.enums.ProductGroup
import harbor.exception.MissingParameterException
import harbor.model.Parameter
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.Clock
import java.time.Instant
import java.time.LocalDate

/**
 * Read and write access to `parameter_set` for every calculation, service and the admin page.
 *
 * Lookups load the versions in force today and the most specific matching scope wins
 * (product group + country + scope value > product group + country > product group > global); among equal
 * specificity the newest `valid_from` wins. Values are read per call; the table is tiny and changed rarely,
 * so no cache is kept (a cache would also have to be invalidated across instances).
 */
@Service
class ParameterService(
    private val parameterDao: ParameterDao,
    private val clock: Clock,
) {

    data class Upsert(
        val scopeProductGroup: ProductGroup?,
        val scopeCountry: String?,
        val scopeValue: String?,
        val value: BigDecimal,
        val validFrom: LocalDate?,
        val updatedBy: String,
    )

    @Transactional(readOnly = true)
    fun find(key: ParameterKey, productGroup: ProductGroup? = null, country: String? = null, scopeValue: String? = null): BigDecimal? =
        parameterDao.findInForce(key.key, LocalDate.now(clock))
            .filter { it.matches(productGroup, country, scopeValue) }
            .sortedWith(compareByDescending<Parameter> { it.specificity }.thenByDescending { it.validFrom })
            .firstOrNull()
            ?.value

    fun required(key: ParameterKey, productGroup: ProductGroup? = null, country: String? = null, scopeValue: String? = null): BigDecimal =
        find(key, productGroup, country, scopeValue) ?: throw MissingParameterException(key.key, productGroup, country, scopeValue)

    /** All values of a key in force today, keyed by `scope_value` (e.g. handling cost per city). */
    @Transactional(readOnly = true)
    fun byScopeValue(key: ParameterKey, productGroup: ProductGroup? = null): Map<String, BigDecimal> =
        parameterDao.findInForce(key.key, LocalDate.now(clock))
            .filter { it.scopeValue != null && (it.scopeProductGroup == null || it.scopeProductGroup == productGroup) }
            .groupBy { it.scopeValue!! }
            .mapValues { (_, versions) -> versions.maxWith(compareBy<Parameter> { it.specificity }.thenBy { it.validFrom }).value }

    @Transactional(readOnly = true)
    fun list(productGroup: ProductGroup?): List<Parameter> = parameterDao.findAllForProductGroup(productGroup)

    /** Creates a new version of the key for the given scope and valid_from, or updates the value of an existing one. */
    @Transactional
    fun upsert(key: ParameterKey, upsert: Upsert): Parameter {
        val validFrom = upsert.validFrom ?: LocalDate.now(clock)
        val country = upsert.scopeCountry?.uppercase()
        val now = Instant.now(clock)
        val existing = parameterDao.findByKeyAndScopeProductGroupAndScopeCountryAndScopeValueAndValidFrom(
            key.key, upsert.scopeProductGroup, country, upsert.scopeValue, validFrom,
        )
        if (existing != null) {
            existing.value = upsert.value
            existing.updatedBy = upsert.updatedBy
            existing.updatedAt = now
            return existing
        }
        return parameterDao.save(
            Parameter(
                key = key.key,
                scopeProductGroup = upsert.scopeProductGroup,
                scopeCountry = country,
                scopeValue = upsert.scopeValue,
                value = upsert.value,
                validFrom = validFrom,
                updatedBy = upsert.updatedBy,
                updatedAt = now,
            ),
        )
    }
}
