package com.acme.harbor.api

import com.acme.harbor.api.generated.MarketApi
import com.acme.harbor.api.generated.model.BaselinePricesDto
import com.acme.harbor.api.generated.model.ScenarioDto
import com.acme.harbor.api.generated.model.ScenarioInputDto
import com.acme.harbor.context.SessionContext
import com.acme.harbor.manager.MarketManager
import com.acme.harbor.mapper.ScenarioMapper
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID

/**
 * REST adapter for the `market` tag (session-scoped). Mappings are on the generated [MarketApi] interface.
 * The `xHarborSession` parameter is declared by the contract; the session itself is read from
 * `SessionContext.current()` (bound by `SessionHeaderFilter`).
 */
@RestController
class ScenarioController(private val manager: MarketManager) : MarketApi {

    override fun listScenarios(xHarborSession: UUID): ResponseEntity<List<ScenarioDto>> =
        ResponseEntity.ok(manager.listScenarios(SessionContext.current()).map(ScenarioMapper::scenario))

    override fun createScenario(xHarborSession: UUID, scenarioInput: ScenarioInputDto): ResponseEntity<ScenarioDto> {
        val scenario = manager.createScenario(SessionContext.current(), ScenarioMapper.input(scenarioInput))
        return ResponseEntity.status(HttpStatus.CREATED).body(ScenarioMapper.scenario(scenario))
    }

    override fun updateScenario(xHarborSession: UUID, scenarioId: UUID, scenarioInput: ScenarioInputDto): ResponseEntity<ScenarioDto> {
        val scenario = manager.updateScenario(SessionContext.current(), scenarioId, ScenarioMapper.input(scenarioInput))
        return ResponseEntity.ok(ScenarioMapper.scenario(scenario))
    }

    override fun deleteScenario(xHarborSession: UUID, scenarioId: UUID): ResponseEntity<Unit> {
        manager.deleteScenario(SessionContext.current(), scenarioId)
        return ResponseEntity.noContent().build()
    }

    override fun getBaselinePrices(xHarborSession: UUID): ResponseEntity<BaselinePricesDto> =
        ResponseEntity.ok(ScenarioMapper.baseline(manager.baseline(SessionContext.current())))
}
