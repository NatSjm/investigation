package com.acme.harbor.service

import com.acme.harbor.context.SessionScope
import com.acme.harbor.dao.repository.MarketScenarioRepository
import com.acme.harbor.enums.ScenarioKind
import com.acme.harbor.exception.NotFoundException
import com.acme.harbor.dao.model.MarketScenario
import com.acme.harbor.model.ScenarioShock
import com.acme.harbor.validator.ScenarioValidator
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
    private val scenarioRepository: MarketScenarioRepository,
    private val validator: ScenarioValidator,
    private val clock: Clock,
) {

    data class ScenarioInput(val name: String, val kind: ScenarioKind, val shocks: List<ScenarioShock>)

    fun list(scope: SessionScope): List<MarketScenario> = scenarioRepository.findAllBySessionIdOrderByCreatedAt(scope.sessionId)

    @Transactional
    fun create(scope: SessionScope, input: ScenarioInput): MarketScenario {
        validator.validate(input.name, input.shocks, scope.horizonMonths)
        validator.validateCount(scenarioRepository.countBySessionId(scope.sessionId))
        return scenarioRepository.save(
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
    fun delete(scope: SessionScope, scenarioId: UUID) = scenarioRepository.delete(load(scope, scenarioId))

    private fun load(scope: SessionScope, scenarioId: UUID): MarketScenario =
        scenarioRepository.findByIdAndSessionId(scenarioId, scope.sessionId)
            ?: throw NotFoundException("Scenario", scenarioId)
}
