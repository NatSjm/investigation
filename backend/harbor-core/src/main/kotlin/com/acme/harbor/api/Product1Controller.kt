package com.acme.harbor.api

import com.acme.harbor.api.generated.Product1Api
import com.acme.harbor.api.generated.model.MovementInputListDto
import com.acme.harbor.api.generated.model.PeerSimulationRequestDto
import com.acme.harbor.api.generated.model.PeerSimulationResultDto
import com.acme.harbor.api.generated.model.ProductOverviewDto
import com.acme.harbor.api.generated.model.ProjectionDto
import com.acme.harbor.context.SessionContext
import com.acme.harbor.manager.Product1Manager
import com.acme.harbor.mapper.ProjectionMapper
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID

/**
 * REST adapter for the `product1` tag (all session-scoped). Mappings are on the generated [Product1Api];
 * the `xHarborSession` header parameter is part of the contract but the session is taken from
 * `SessionContext.current()`, which `SessionHeaderFilter` has bound and validated.
 */
@RestController
class Product1Controller(private val manager: Product1Manager) : Product1Api {

    override fun getProduct1Overview(xHarborSession: UUID, city: String?): ResponseEntity<ProductOverviewDto> {
        val scope = SessionContext.current()
        return ResponseEntity.ok(ProjectionMapper.overview(scope, manager.overview(scope, city)))
    }

    override fun putProduct1Movements(xHarborSession: UUID, movementInputList: MovementInputListDto): ResponseEntity<ProjectionDto> {
        val scope = SessionContext.current()
        val tables = manager.replaceMovements(scope, ProjectionMapper.movementInputs(movementInputList))
        return ResponseEntity.ok(ProjectionMapper.projection(scope, tables))
    }

    override fun postProduct1PeerSimulation(xHarborSession: UUID, peerSimulationRequest: PeerSimulationRequestDto): ResponseEntity<PeerSimulationResultDto> {
        val scope = SessionContext.current()
        val result = manager.peerSimulation(scope, peerSimulationRequest.peerSegment, peerSimulationRequest.scalingFactor)
        return ResponseEntity.ok(ProjectionMapper.peerResult(result))
    }

    override fun getProduct1Projection(xHarborSession: UUID): ResponseEntity<ProjectionDto> {
        val scope = SessionContext.current()
        return ResponseEntity.ok(ProjectionMapper.projection(scope, manager.projection(scope)))
    }
}
