package harbor.dao

import harbor.enums.ProductGroup
import harbor.model.Parameter
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.time.LocalDate
import java.util.UUID

/** Versioned parameter values (table `parameter_set`). */
@Repository
interface ParameterDao : JpaRepository<Parameter, UUID> {

    /** All versions of a key that are in force at [asOf] (newest first per scope; ParameterService picks the best match). */
    @Query("select p from Parameter p where p.key = :key and p.validFrom <= :asOf order by p.validFrom desc")
    fun findInForce(key: String, asOf: LocalDate): List<Parameter>

    @Query(
        """
        select p from Parameter p
        where (:productGroup is null or p.scopeProductGroup is null or p.scopeProductGroup = :productGroup)
        order by p.key, p.scopeProductGroup, p.scopeCountry, p.scopeValue, p.validFrom desc
        """,
    )
    fun findAllForProductGroup(productGroup: ProductGroup?): List<Parameter>

    fun findByKeyAndScopeProductGroupAndScopeCountryAndScopeValueAndValidFrom(
        key: String,
        scopeProductGroup: ProductGroup?,
        scopeCountry: String?,
        scopeValue: String?,
        validFrom: LocalDate,
    ): Parameter?
}
