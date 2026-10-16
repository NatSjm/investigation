package com.acme.harbor.service

import com.acme.harbor.dao.repository.ParameterRepository
import com.acme.harbor.enums.ParameterKey
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.exception.MissingParameterException
import com.acme.harbor.dao.model.Parameter
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
    private val parameterRepository: ParameterRepository,
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
        parameterRepository.findInForce(key.key, LocalDate.now(clock))
            .filter { it.matches(productGroup, country, scopeValue) }
            .sortedWith(compareByDescending<Parameter> { it.specificity }.thenByDescending { it.validFrom })
            .firstOrNull()
            ?.value

    fun required(key: ParameterKey, productGroup: ProductGroup? = null, country: String? = null, scopeValue: String? = null): BigDecimal =
        find(key, productGroup, country, scopeValue) ?: throw MissingParameterException(key.key, productGroup, country, scopeValue)

    /** All values of a key in force today, keyed by `scope_value` (e.g. handling cost per city). */
    @Transactional(readOnly = true)
    fun byScopeValue(key: ParameterKey, productGroup: ProductGroup? = null): Map<String, BigDecimal> =
        parameterRepository.findInForce(key.key, LocalDate.now(clock))
            .filter { it.scopeValue != null && (it.scopeProductGroup == null || it.scopeProductGroup == productGroup) }
            .groupBy { it.scopeValue!! }
            .mapValues { (_, versions) -> versions.maxWith(compareBy<Parameter> { it.specificity }.thenBy { it.validFrom }).value }

    @Transactional(readOnly = true)
    fun list(productGroup: ProductGroup?): List<Parameter> = parameterRepository.findAllForProductGroup(productGroup)

    /** Creates a new version of the key for the given scope and valid_from, or updates the value of an existing one. */
    @Transactional
    fun upsert(key: ParameterKey, upsert: Upsert): Parameter {
        val validFrom = upsert.validFrom ?: LocalDate.now(clock)
        val country = upsert.scopeCountry?.uppercase()
        val now = Instant.now(clock)
        val existing = parameterRepository.findByKeyAndScopeProductGroupAndScopeCountryAndScopeValueAndValidFrom(
            key.key, upsert.scopeProductGroup, country, upsert.scopeValue, validFrom,
        )
        if (existing != null) {
            existing.value = upsert.value
            existing.updatedBy = upsert.updatedBy
            existing.updatedAt = now
            return existing
        }
        return parameterRepository.save(
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
