package harbor.service

import harbor.context.SessionScope
import harbor.dao.MovementMonthlyDao
import harbor.dao.SessionMovementInputDao
import harbor.enums.ParameterKey
import harbor.model.MovementMonthly
import harbor.utils.MonthGrid
import harbor.utils.ProjectionAggregator.Context
import harbor.utils.ProjectionAggregator.Row
import harbor.utils.toPeriodDate
import harbor.utils.toYearMonth
import org.springframework.stereotype.Component
import java.math.BigDecimal
import java.time.Clock
import java.time.LocalDate
import java.time.YearMonth

/**
 * Turns the data of a session into the flat row list and the parameter context of `ProjectionAggregator`.
 *
 * Rows per horizon month:
 * - months with modelled inputs (`session_movement_input`) use those inputs only;
 * - every other month carries the actual movements of the same calendar month one year earlier forward
 *   (`movement_monthly`, average unit price = value / quantity), i.e. the last 12 full months repeat.
 *
 * Context: `priceIndex` from the baseline curve ([BaselinePriceService]), `tariff.rate` per product group and
 * price basis, `handling.cost` per city and `transport.cost` per transport mode from `parameter_set`.
 */
@Component
class ProjectionInputAssembler(
    private val monthlyDao: MovementMonthlyDao,
    private val inputDao: SessionMovementInputDao,
    private val parameters: ParameterService,
    private val curves: BaselinePriceService,
    private val clock: Clock,
) {

    fun grid(scope: SessionScope): MonthGrid = MonthGrid.startingAfter(LocalDate.now(clock), scope.horizonMonths)

    fun rows(scope: SessionScope, grid: MonthGrid): List<Row> {
        val modelled = inputDao.findAllBySessionIdOrderByPeriod(scope.sessionId).groupBy { it.period.toYearMonth() }
        val lookback = MonthGrid.lastFullMonths(LocalDate.now(clock))
        val actual = monthlyDao.findAllByClientIdAndProductGroupAndPeriodBetween(
            scope.clientId, scope.productGroup, lookback.first().toPeriodDate(), lookback.last().toPeriodDate(),
        ).groupBy { it.period.toYearMonth() }

        return grid.months.flatMap { month ->
            modelled[month]?.map { input ->
                Row(month, input.subProduct, input.city, input.transportMode, input.direction, input.quantity, input.unitPrice, scope.priceBasis)
            } ?: carriedForward(month, actual, scope)
        }
    }

    private fun carriedForward(month: YearMonth, actual: Map<YearMonth, List<MovementMonthly>>, scope: SessionScope): List<Row> =
        actual[month.minusYears(1)].orEmpty().map { m ->
            Row(month, m.subProduct, m.city, m.transportMode, m.direction, m.quantity, m.averageUnitPrice, scope.priceBasis)
        }

    fun context(scope: SessionScope, grid: MonthGrid): Context {
        val curve = curves.curve(scope.productGroup, grid)
        val handling = parameters.byScopeValue(ParameterKey.HANDLING_COST, scope.productGroup)
        val transport = parameters.byScopeValue(ParameterKey.TRANSPORT_COST, scope.productGroup)
        return Context(
            priceIndex = curve.priceIndex(grid),
            tariffRate = { basis -> parameters.find(ParameterKey.TARIFF_RATE, scope.productGroup, basis.name) ?: BigDecimal.ZERO },
            handlingCost = { city -> city?.let { handling[it] } ?: BigDecimal.ZERO },
            transportCost = { mode -> mode?.let { transport[it.name] } ?: BigDecimal.ZERO },
        )
    }
}
