package com.acme.harbor.manager

import com.acme.harbor.context.SessionScope
import com.acme.harbor.dao.model.MarketScenario
import com.acme.harbor.service.BaselinePriceService
import com.acme.harbor.service.ScenarioService
import com.acme.harbor.utils.MonthGrid
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.Clock
import java.time.LocalDate
import java.util.UUID

/**
 * Market scenarios of the current session (create / update / delete, with shocks validated against the
 * session horizon by `ScenarioValidator`) and the baseline price curve from `baseline_price` (fed by market-data).
 * Everything here is scoped by the session the controller reads from `SessionContext.current()` (resolved by `SessionHeaderFilter`).
 *
 * @docs MKT-001
 */
@Service
class MarketManager(
    private val scenarioService: ScenarioService,
    private val curves: BaselinePriceService,
    private val clock: Clock,
) {

    @Transactional(readOnly = true)
    fun listScenarios(scope: SessionScope): List<MarketScenario> = scenarioService.list(scope)

    @Transactional
    fun createScenario(scope: SessionScope, input: ScenarioService.ScenarioInput): MarketScenario =
        scenarioService.create(scope, input)

    @Transactional
    fun updateScenario(scope: SessionScope, scenarioId: UUID, input: ScenarioService.ScenarioInput): MarketScenario =
        scenarioService.update(scope, scenarioId, input)

    @Transactional
    fun deleteScenario(scope: SessionScope, scenarioId: UUID) = scenarioService.delete(scope, scenarioId)

    @Transactional
    fun baseline(scope: SessionScope): BaselinePriceService.Curve {
        return curves.curve(scope.productGroup, MonthGrid.startingAfter(LocalDate.now(clock), scope.horizonMonths))
    }
}
