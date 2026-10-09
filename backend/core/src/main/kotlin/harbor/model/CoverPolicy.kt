package harbor.model

import harbor.utils.CoverRatioCalculator
import harbor.utils.toYearMonth
import harbor.enums.ProductGroup
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

/**
 * A cover policy of a client (table `cover_policy`, V6__cover.sql): covers `covered_share` of the value of
 * one sub-product (or of the whole product group when `sub_product` is null) between `valid_from` and
 * `valid_to` against `premium_rate`.
 */
@Entity
@Table(name = "cover_policy")
class CoverPolicy(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "client_id", nullable = false)
    val clientId: UUID,

    @Enumerated(EnumType.STRING)
    @Column(name = "product_group", nullable = false)
    val productGroup: ProductGroup,

    @Column(name = "sub_product")
    val subProduct: String?,

    @Column(name = "covered_share", nullable = false)
    val coveredShare: BigDecimal,

    @Column(name = "premium_rate", nullable = false)
    val premiumRate: BigDecimal,

    @Column(name = "valid_from", nullable = false)
    val validFrom: LocalDate,

    @Column(name = "valid_to")
    val validTo: LocalDate?,
) {
    fun toTerms() = CoverRatioCalculator.PolicyTerms(
        subProduct = subProduct,
        coveredShare = coveredShare,
        validFrom = validFrom.toYearMonth(),
        validTo = validTo?.toYearMonth(),
    )
}
