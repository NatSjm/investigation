package com.acme.harbor.dao.model

import com.acme.harbor.enums.ProductGroup
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.Instant
import java.time.LocalDate
import java.util.UUID

/**
 * One value of a parameter (table `parameter_set`, V9__parameters.sql). The scope columns narrow a value
 * to a product group, a country (price basis) and/or a scope value such as a city or transport mode;
 * `valid_from` versions the value over time. Keys are listed in `com.acme.harbor.enums.ParameterKey` (blueprint section 3.4).
 */
@Entity
@Table(name = "parameter_set")
class Parameter(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "key", nullable = false)
    val key: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "scope_product_group")
    val scopeProductGroup: ProductGroup? = null,

    @Column(name = "scope_country")
    val scopeCountry: String? = null,

    @Column(name = "scope_value")
    val scopeValue: String? = null,

    @Column(name = "value", nullable = false)
    var value: BigDecimal,

    @Column(name = "valid_from", nullable = false)
    val validFrom: LocalDate,

    @Column(name = "updated_by", nullable = false)
    var updatedBy: String,

    @Column(name = "updated_at", nullable = false)
    var updatedAt: Instant,
) {
    /** Number of scope columns set; the provider prefers the most specific match. */
    val specificity: Int
        get() = listOf(scopeProductGroup, scopeCountry, scopeValue).count { it != null }

    fun matches(productGroup: ProductGroup?, country: String?, scopeValue: String?): Boolean =
        (scopeProductGroup == null || scopeProductGroup == productGroup) &&
            (scopeCountry == null || scopeCountry.equals(country, ignoreCase = true)) &&
            (this.scopeValue == null || this.scopeValue.equals(scopeValue, ignoreCase = true))
}
