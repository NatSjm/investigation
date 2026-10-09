package harbor.model

import harbor.enums.ProductGroup
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.Instant
import java.time.LocalDate

/**
 * One month of the baseline curve of a product group / corridor (table `baseline_price`,
 * V7__market_stress.sql), fed by the market-data service via `harbor.market.prices-updated`.
 */
@Entity
@Table(name = "baseline_price")
class BaselinePrice(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    val id: Long? = null,

    @Enumerated(EnumType.STRING)
    @Column(name = "product_group", nullable = false)
    val productGroup: ProductGroup,

    @Column(name = "corridor", nullable = false)
    val corridor: String,

    @Column(name = "period", nullable = false)
    val period: LocalDate,

    @Column(name = "price", nullable = false)
    var price: BigDecimal,

    @Column(name = "transport_price", nullable = false)
    var transportPrice: BigDecimal,

    @Column(name = "as_of", nullable = false)
    var asOf: Instant,
)
