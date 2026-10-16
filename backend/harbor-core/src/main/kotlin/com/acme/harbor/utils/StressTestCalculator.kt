package com.acme.harbor.utils

import com.acme.harbor.enums.ClientRole
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Monthly stress test per scenario and dimension value (city for Product 1, transport mode for Product 2).
 *
 * Definition, per scenario `s`, month `m` and dimension value:
 * - `sign = +1` for `IMPORTER`, `-1` for `EXPORTER`; for `MIXED` (and `UNDETERMINED`) the net direction
 *   quantity is used instead: `signedQty = uncoveredInbound - uncoveredOutbound`
 * - `uncoveredQty = uncoveredInbound + uncoveredOutbound` (quantity not covered by a policy)
 * - `exposure = uncoveredQty * (price_s(m) - baseline(m)) * sign`
 * - `transportCostDelta = totalQty * (transport_s(m) - transportBaseline(m))`
 * - `cumulativeExposure` = running sum over months of `exposure + transportCostDelta`, per dimension value
 * - all outputs money, scale 2, `HALF_EVEN` (`stress.rounding_scale`)
 *
 * `price_s` / `transport_s` are produced by [ScenarioPricePath]. Worked examples: `StressTestCalculatorTest`.
 *
 * @docs stress_test_monthly
 */
object StressTestCalculator {

    data class MonthInput(
        val period: YearMonth,
        val dimensionValue: String,
        val uncoveredInboundQty: BigDecimal,
        val uncoveredOutboundQty: BigDecimal,
        /** Total quantity moved in the month (covered or not); drives the transport cost delta. */
        val totalQty: BigDecimal,
        val baselinePrice: BigDecimal,
        val scenarioPrice: BigDecimal,
        val baselineTransportPrice: BigDecimal,
        val scenarioTransportPrice: BigDecimal,
    )

    data class MonthResult(
        val period: YearMonth,
        val dimensionValue: String,
        val scenarioPrice: BigDecimal,
        val scenarioTransportPrice: BigDecimal,
        val exposure: BigDecimal,
        val transportCostDelta: BigDecimal,
        val cumulativeExposure: BigDecimal,
    )

    /** Quantity with the sign that makes a price increase positive for an importer and negative for an exporter. */
    fun signedUncoveredQty(role: ClientRole, inbound: BigDecimal, outbound: BigDecimal): BigDecimal = when (role) {
        ClientRole.IMPORTER -> inbound + outbound
        ClientRole.EXPORTER -> (inbound + outbound).negate()
        ClientRole.MIXED, ClientRole.UNDETERMINED -> inbound - outbound
    }

    fun exposure(role: ClientRole, input: MonthInput): BigDecimal =
        (signedUncoveredQty(role, input.uncoveredInboundQty, input.uncoveredOutboundQty) *
            (input.scenarioPrice - input.baselinePrice)).money()

    fun transportCostDelta(input: MonthInput): BigDecimal =
        (input.totalQty * (input.scenarioTransportPrice - input.baselineTransportPrice)).money()

    /** Results ordered by dimension value then period; the cumulative exposure runs per dimension value. */
    fun run(role: ClientRole, inputs: List<MonthInput>): List<MonthResult> =
        inputs.groupBy { it.dimensionValue }.entries.sortedBy { it.key }.flatMap { (_, months) ->
            var cumulative = BigDecimal.ZERO
            months.sortedBy { it.period }.map { input ->
                val exposure = exposure(role, input)
                val delta = transportCostDelta(input)
                cumulative += exposure + delta
                MonthResult(
                    period = input.period,
                    dimensionValue = input.dimensionValue,
                    scenarioPrice = input.scenarioPrice,
                    scenarioTransportPrice = input.scenarioTransportPrice,
                    exposure = exposure,
                    transportCostDelta = delta,
                    cumulativeExposure = cumulative.money(),
                )
            }
        }
}
