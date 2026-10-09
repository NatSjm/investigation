package harbor.service

import harbor.context.SessionScope
import harbor.dao.MarketScenarioDao
import harbor.enums.ScenarioKind
import harbor.exception.NotFoundException
import harbor.model.MarketScenario
import harbor.model.ScenarioShock
import harbor.validator.ScenarioValidator
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.Clock
import java.time.Instant
import java.util.UUID

/**
 * Market scenarios of a session (`market_scenario`): create / update / delete with the shocks validated
 * against the session horizon by [ScenarioValidator]; shocks are stored ordered by `fromMonth`.
 */
@Service
class ScenarioService(
    private val scenarioDao: MarketScenarioDao,
    private val validator: ScenarioValidator,
    private val clock: Clock,
) {

    data class ScenarioInput(val name: String, val kind: ScenarioKind, val shocks: List<ScenarioShock>)

    fun list(scope: SessionScope): List<MarketScenario> = scenarioDao.findAllBySessionIdOrderByCreatedAt(scope.sessionId)

    @Transactional
    fun create(scope: SessionScope, input: ScenarioInput): MarketScenario {
        validator.validate(input.name, input.shocks, scope.horizonMonths)
        validator.validateCount(scenarioDao.countBySessionId(scope.sessionId))
        return scenarioDao.save(
            MarketScenario(
                sessionId = scope.sessionId,
                name = input.name.trim(),
                kind = input.kind,
                shocks = input.shocks.sortedBy { it.fromMonth },
                createdBy = scope.representativeId,
                createdAt = Instant.now(clock),
            ),
        )
    }

    @Transactional
    fun update(scope: SessionScope, scenarioId: UUID, input: ScenarioInput): MarketScenario {
        validator.validate(input.name, input.shocks, scope.horizonMonths)
        val scenario = load(scope, scenarioId)
        scenario.name = input.name.trim()
        scenario.kind = input.kind
        scenario.shocks = input.shocks.sortedBy { it.fromMonth }
        return scenario
    }

    @Transactional
    fun delete(scope: SessionScope, scenarioId: UUID) = scenarioDao.delete(load(scope, scenarioId))

    private fun load(scope: SessionScope, scenarioId: UUID): MarketScenario =
        scenarioDao.findByIdAndSessionId(scenarioId, scope.sessionId)
            ?: throw NotFoundException("Scenario", scenarioId)
}
