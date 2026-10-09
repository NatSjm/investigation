package harbor.model

import harbor.enums.Direction
import harbor.enums.PriceBasis
import harbor.enums.ProductGroup
import harbor.enums.TransportMode
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

/**
 * One actual movement line from a daily XLS file (table `goods_movement`, V3__movements.sql).
 * `period` is the first day of the month the movement belongs to.
 */
@Entity
@Table(name = "goods_movement")
class GoodsMovement(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    val id: Long? = null,

    @Column(name = "client_id", nullable = false)
    val clientId: UUID,

    @Column(name = "batch_id", nullable = false)
    val batchId: UUID,

    @Enumerated(EnumType.STRING)
    @Column(name = "product_group", nullable = false)
    val productGroup: ProductGroup,

    @Column(name = "sub_product", nullable = false)
    val subProduct: String,

    @Column(name = "city")
    val city: String?,

    @Enumerated(EnumType.STRING)
    @Column(name = "transport_mode")
    val transportMode: TransportMode?,

    @Enumerated(EnumType.STRING)
    @Column(name = "direction", nullable = false)
    val direction: Direction,

    @Column(name = "period", nullable = false)
    val period: LocalDate,

    @Column(name = "quantity", nullable = false)
    val quantity: BigDecimal,

    @Column(name = "unit_price", nullable = false)
    val unitPrice: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(name = "price_basis", nullable = false)
    val priceBasis: PriceBasis,
)
