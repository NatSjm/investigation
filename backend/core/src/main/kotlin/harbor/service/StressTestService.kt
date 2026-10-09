package harbor.service

import harbor.context.SessionScope
import harbor.enums.ClientRole
import harbor.enums.Direction
import harbor.enums.StressDimension
import harbor.model.MarketScenario
import harbor.utils.CoverRatioCalculator
import harbor.utils.ProjectionAggregator
import harbor.utils.ScenarioPricePath
import harbor.utils.StressTestCalculator
import harbor.utils.StressTestCalculator.MonthInput
import org.springframework.stereotype.Service
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Prepares the inputs of calculation `stress_test_monthly` for one session and runs it per scenario:
 *
 * 1. the flat projection rows of the session (same [ProjectionInputAssembler] as the projection tables),
 * 2. the uncovered quantity of each row = `quantity * (1 - coveredShare of the matching policy in m)`,
 * 3. grouped per month and dimension value (city or transport mode) into inbound / outbound / total,
 * 4. scenario price and transport paths from the baseline curve (`scenario_price_path`),
 * 5. `StressTestCalculator.run` with the session role.
 */
@Service
class StressTestService(
    private val assembler: ProjectionInputAssembler,
    private val curves: BaselinePriceService,
    private val coverRatioService: CoverRatioService,
) {

    data class ScenarioRun(val scenario: MarketScenario, val rows: List<StressTestCalculator.MonthResult>)

    fun run(scope: SessionScope, role: ClientRole, scenarios: List<MarketScenario>, dimension: StressDimension): List<ScenarioRun> {
        val grid = assembler.grid(scope)
        val rows = assembler.rows(scope, grid)
        val policies = coverRatioService.policies(scope.clientId, scope.productGroup)
        val curve = curves.curve(scope.productGroup, grid)
        val quantities = quantities(rows, policies, dimension)

        return scenarios.map { scenario ->
            val path = ScenarioPricePath.path(curve.prices(grid), curve.transportPrices(grid), scenario.calcShocks())
            val inputs = quantities.map { (key, q) ->
                val index = grid.indexOf(key.first)!! - 1
                MonthInput(
                    period = key.first,
                    dimensionValue = key.second,
                    uncoveredInboundQty = q.uncoveredIn,
                    uncoveredOutboundQty = q.uncoveredOut,
                    totalQty = q.total,
                    baselinePrice = curve.price(key.first),
                    scenarioPrice = path.prices[index],
                    baselineTransportPrice = curve.transportPrice(key.first),
                    scenarioTransportPrice = path.transportPrices[index],
                )
            }
            ScenarioRun(scenario, StressTestCalculator.run(role, inputs))
        }
    }

    private data class Quantities(val uncoveredIn: BigDecimal, val uncoveredOut: BigDecimal, val total: BigDecimal)

    private fun quantities(
        rows: List<ProjectionAggregator.Row>,
        policies: List<CoverRatioCalculator.PolicyTerms>,
        dimension: StressDimension,
    ): Map<Pair<YearMonth, String>, Quantities> =
        rows.groupBy { it.period to ProjectionAggregator.dimensionValue(it, dimension.dimensionKind) }
            .mapValues { (_, group) ->
                var inbound = BigDecimal.ZERO
                var outbound = BigDecimal.ZERO
                var total = BigDecimal.ZERO
                group.forEach { row ->
                    val uncovered = row.quantity * (BigDecimal.ONE - CoverRatioCalculator.coveredShare(row.subProduct, row.period, policies))
                    if (row.direction == Direction.IN) inbound += uncovered else outbound += uncovered
                    total += row.quantity
                }
                Quantities(inbound, outbound, total)
            }
}
