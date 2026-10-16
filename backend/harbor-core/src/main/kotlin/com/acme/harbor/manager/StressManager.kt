package com.acme.harbor.manager

import com.acme.harbor.context.SessionScope
import com.acme.harbor.dao.repository.MarketScenarioRepository
import com.acme.harbor.dao.repository.StressTestResultRepository
import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.StressDimension
import com.acme.harbor.dao.model.MarketScenario
import com.acme.harbor.dao.model.StressTestResult
import com.acme.harbor.service.ClientRoleService
import com.acme.harbor.service.StressTestService
import com.acme.harbor.utils.StressTestCalculator
import com.acme.harbor.utils.toPeriodDate
import com.acme.harbor.utils.toYearMonth
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.Clock
import java.time.Instant
import java.util.UUID

/**
 * Stress test of the current session: runs calculation `stress_test_monthly` for every scenario of the
 * session ([StressTestService]) and stores the monthly rows in `stress_test_result` (dimension = city for
 * Product 1, transport mode for Product 2). `get` returns the stored run; asking for the other dimension
 * recomputes on the fly without storing, which is what the page toggle does.
 *
 * @docs STR-001
 */
@Service
class StressManager(
    private val stressTestService: StressTestService,
    private val resultRepository: StressTestResultRepository,
    private val scenarioRepository: MarketScenarioRepository,
    private val roleService: ClientRoleService,
    private val clock: Clock,
) {

    data class ScenarioResult(val scenario: MarketScenario, val rows: List<StressTestCalculator.MonthResult>)

    data class Result(val sessionId: UUID, val dimension: StressDimension, val role: ClientRole, val computedAt: Instant, val scenarios: List<ScenarioResult>)

    @Transactional
    fun run(scope: SessionScope): Result {
        val dimension = StressDimension.defaultFor(scope.productGroup)
        val role = role(scope)
        val runs = stressTestService.run(scope, role, scenarios(scope), dimension)

        resultRepository.deleteAllBySessionId(scope.sessionId)
        resultRepository.saveAll(
            runs.flatMap { run ->
                run.rows.map {
                    StressTestResult(
                        sessionId = scope.sessionId,
                        scenarioId = run.scenario.id,
                        period = it.period.toPeriodDate(),
                        dimensionValue = it.dimensionValue,
                        exposure = it.exposure,
                        transportCostDelta = it.transportCostDelta,
                        cumulativeExposure = it.cumulativeExposure,
                    )
                }
            },
        )
        return Result(scope.sessionId, dimension, role, Instant.now(clock), runs.map { ScenarioResult(it.scenario, it.rows) })
    }

    @Transactional
    fun get(scope: SessionScope, dimension: StressDimension?): Result {
        val stored = StressDimension.defaultFor(scope.productGroup)
        val requested = dimension ?: stored
        if (requested != stored) {
            val runs = stressTestService.run(scope, role(scope), scenarios(scope), requested)
            return Result(scope.sessionId, requested, role(scope), Instant.now(clock), runs.map { ScenarioResult(it.scenario, it.rows) })
        }
        val rows = resultRepository.findAllBySessionIdOrderByScenarioIdAscDimensionValueAscPeriodAsc(scope.sessionId)
        if (rows.isEmpty()) return run(scope)
        val byScenario = rows.groupBy { it.scenarioId }
        return Result(
            sessionId = scope.sessionId,
            dimension = stored,
            role = role(scope),
            computedAt = Instant.now(clock),
            scenarios = scenarios(scope).filter { it.id in byScenario }.map { scenario ->
                ScenarioResult(scenario, byScenario.getValue(scenario.id).map { it.toMonthResult() })
            },
        )
    }

    private fun scenarios(scope: SessionScope): List<MarketScenario> =
        scenarioRepository.findAllBySessionIdOrderByCreatedAt(scope.sessionId)

    private fun role(scope: SessionScope): ClientRole =
        roleService.sessionRole(scope.clientId, scope.productGroup, scope.roleOverride)

    private fun StressTestResult.toMonthResult() = StressTestCalculator.MonthResult(
        period = period.toYearMonth(),
        dimensionValue = dimensionValue,
        scenarioPrice = BigDecimal.ZERO,
        scenarioTransportPrice = BigDecimal.ZERO,
        exposure = exposure,
        transportCostDelta = transportCostDelta,
        cumulativeExposure = cumulativeExposure,
    )
}
