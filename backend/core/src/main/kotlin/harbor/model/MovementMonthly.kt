package harbor.model

import harbor.enums.Direction
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

/**
 * Monthly rollup of `goods_movement` (table `movement_monthly`, V3__movements.sql), written by
 * `MonthlySnapshotJob`. `value = sum(quantity * unit_price)`; the average unit price of a row is
 * `value / quantity`. This is the "actual movements" input of the projection and the role classification.
 */
@Entity
@Table(name = "movement_monthly")
class MovementMonthly(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    val id: Long? = null,

    @Column(name = "client_id", nullable = false)
    val clientId: java.util.UUID,

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

    @Column(name = "value", nullable = false)
    val value: BigDecimal,
) {
    /** Average unit price of the month, scale 4; 0 when nothing was moved. */
    val averageUnitPrice: BigDecimal
        get() = if (quantity.signum() == 0) BigDecimal.ZERO else value.divide(quantity, 4, java.math.RoundingMode.HALF_EVEN)
}
