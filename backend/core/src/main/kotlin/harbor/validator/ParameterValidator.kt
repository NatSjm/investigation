package harbor.validator

import harbor.enums.ParameterKey
import harbor.exception.ValidationException
import harbor.utils.MonthGrid
import org.springframework.stereotype.Component
import java.math.BigDecimal

/**
 * Rules for `upsertParameter` on the admin page:
 * - the key must be one of [ParameterKey] (BLUEPRINT.md section 3.4),
 * - shares, thresholds and rates lie in `0..1`; costs, volumes and factors are not negative,
 * - `projection.horizon_months_default` is a whole number of months in `12..60`,
 * - `stress.rounding_scale` is a whole number in `0..6`.
 */
@Component
class ParameterValidator {

    fun validate(rawKey: String, value: BigDecimal): ParameterKey {
        val key = ParameterKey.fromKey(rawKey) ?: throw ValidationException("Unknown parameter key '$rawKey'")
        when (key) {
            ParameterKey.ROLE_IMPORTER_THRESHOLD, ParameterKey.ROLE_EXPORTER_THRESHOLD,
            ParameterKey.TARIFF_RATE, ParameterKey.COVER_DEFAULT_PREMIUM_RATE ->
                ValidationException.check(value >= BigDecimal.ZERO && value <= BigDecimal.ONE) { "${key.key} must be between 0 and 1" }
            ParameterKey.PROJECTION_HORIZON_MONTHS_DEFAULT ->
                ValidationException.check(isWhole(value) && value.toInt() in MonthGrid.MIN_HORIZON..MonthGrid.MAX_HORIZON) {
                    "${key.key} must be a whole number between ${MonthGrid.MIN_HORIZON} and ${MonthGrid.MAX_HORIZON}"
                }
            ParameterKey.STRESS_ROUNDING_SCALE ->
                ValidationException.check(isWhole(value) && value.toInt() in 0..MAX_ROUNDING_SCALE) { "${key.key} must be a whole number between 0 and $MAX_ROUNDING_SCALE" }
            ParameterKey.ROLE_MIN_VOLUME, ParameterKey.HANDLING_COST, ParameterKey.TRANSPORT_COST, ParameterKey.PEER_SCALING_DEFAULT ->
                ValidationException.check(value.signum() >= 0) { "${key.key} must not be negative" }
        }
        return key
    }

    private fun isWhole(value: BigDecimal): Boolean = value.stripTrailingZeros().scale() <= 0

    companion object {
        const val MAX_ROUNDING_SCALE = 6
    }
}
