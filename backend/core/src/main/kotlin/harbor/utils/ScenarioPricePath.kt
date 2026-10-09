package harbor.utils

import java.math.BigDecimal

/**
 * Scenario price path: applies the shocks of a market scenario to a baseline curve.
 *
 * Definition (per month `m`, 1-based index in the horizon):
 * - `price_s(m) = baseline(m) * prod(1 + shock.priceChangePct)` over all shocks with `fromMonth <= m`
 * - `transportPrice_s(m) = transportBaseline(m) * prod(1 + shock.transportChangePct)` likewise
 *
 * Shocks are cumulative (multiplicative), persist until the end of the horizon and may be defined in any
 * order. Intermediate factors are not rounded; the resulting prices are money (scale 2, HALF_EVEN).
 * Worked example: baseline [10,10,10,10], shocks +10% from month 2 and +5% from month 3 ->
 * [10.00, 11.00, 11.55, 11.55] (see `ScenarioPricePathTest`).
 *
 * @docs scenario_price_path
 */
object ScenarioPricePath {

    /** One shock of a scenario; percentages are fractions (0.10 = +10 %). */
    data class Shock(
        val fromMonth: Int,
        val priceChangePct: BigDecimal = BigDecimal.ZERO,
        val transportChangePct: BigDecimal = BigDecimal.ZERO,
    ) {
        init {
            require(fromMonth >= 1) { "fromMonth is a 1-based month index, was $fromMonth" }
        }
    }

    data class Path(val prices: List<BigDecimal>, val transportPrices: List<BigDecimal>)

    fun pricePath(baseline: List<BigDecimal>, shocks: List<Shock>): List<BigDecimal> =
        apply(baseline, shocks) { it.priceChangePct }

    fun transportPath(transportBaseline: List<BigDecimal>, shocks: List<Shock>): List<BigDecimal> =
        apply(transportBaseline, shocks) { it.transportChangePct }

    fun path(baseline: List<BigDecimal>, transportBaseline: List<BigDecimal>, shocks: List<Shock>): Path =
        Path(pricePath(baseline, shocks), transportPath(transportBaseline, shocks))

    /** Cumulative multiplier in effect at month [month] (1-based). */
    fun factorAt(month: Int, shocks: List<Shock>, change: (Shock) -> BigDecimal): BigDecimal =
        shocks.filter { it.fromMonth <= month }
            .fold(BigDecimal.ONE) { acc, shock -> acc * (BigDecimal.ONE + change(shock)) }

    private fun apply(baseline: List<BigDecimal>, shocks: List<Shock>, change: (Shock) -> BigDecimal): List<BigDecimal> =
        baseline.mapIndexed { index, base -> (base * factorAt(index + 1, shocks, change)).money() }
}
