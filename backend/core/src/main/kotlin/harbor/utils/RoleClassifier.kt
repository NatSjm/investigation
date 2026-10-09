package harbor.utils

import harbor.enums.ClientRole
import harbor.enums.Direction
import java.math.BigDecimal

/**
 * Client role classification for one product group from the last 12 full months of actual movements.
 *
 * Definition:
 * - `inbound = sum(quantity, direction = IN)`, `outbound = sum(quantity, direction = OUT)`
 * - if `inbound + outbound < role.min_volume` -> `UNDETERMINED`
 * - `share = inbound / (inbound + outbound)` (scale 4, HALF_EVEN)
 * - `share >= role.importer_threshold` -> `IMPORTER`
 * - `share <= role.exporter_threshold` -> `EXPORTER`
 * - otherwise `MIXED`
 *
 * Thresholds come from `parameter_set` (`role.min_volume` = 100, `role.importer_threshold` = 0.65,
 * `role.exporter_threshold` = 0.35). Boundaries are inclusive: total exactly `min_volume` is classified,
 * share exactly 0.65 is `IMPORTER`. Worked examples: see `RoleClassifierTest`.
 *
 * @docs client_role_classification
 */
object RoleClassifier {

    data class Thresholds(
        val minVolume: BigDecimal = bd(100),
        val importerThreshold: BigDecimal = bd("0.65"),
        val exporterThreshold: BigDecimal = bd("0.35"),
    ) {
        init {
            require(exporterThreshold <= importerThreshold) { "exporterThreshold must not exceed importerThreshold" }
        }
    }

    /** One actual movement (or monthly rollup) that contributes to the classification. */
    data class Movement(val direction: Direction, val quantity: BigDecimal)

    data class Result(
        val role: ClientRole,
        val inbound: BigDecimal,
        val outbound: BigDecimal,
        /** Inbound share of the total, scale 4; null when the total is below the minimum volume. */
        val share: BigDecimal?,
    )

    fun classify(movements: Iterable<Movement>, thresholds: Thresholds = Thresholds()): Result {
        val inbound = movements.filter { it.direction == Direction.IN }.fold(BigDecimal.ZERO) { a, m -> a + m.quantity }
        val outbound = movements.filter { it.direction == Direction.OUT }.fold(BigDecimal.ZERO) { a, m -> a + m.quantity }
        return classify(inbound, outbound, thresholds)
    }

    fun classify(inbound: BigDecimal, outbound: BigDecimal, thresholds: Thresholds = Thresholds()): Result {
        require(inbound.signum() >= 0 && outbound.signum() >= 0) { "quantities must not be negative" }
        val total = inbound + outbound
        if (total < thresholds.minVolume) {
            return Result(ClientRole.UNDETERMINED, inbound, outbound, share = null)
        }
        val share = Rounding.divideAsRatio(inbound, total)
        val role = when {
            share >= thresholds.importerThreshold -> ClientRole.IMPORTER
            share <= thresholds.exporterThreshold -> ClientRole.EXPORTER
            else -> ClientRole.MIXED
        }
        return Result(role, inbound, outbound, share)
    }
}
