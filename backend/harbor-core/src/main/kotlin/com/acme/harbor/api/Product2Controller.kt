package com.acme.harbor.api

import com.acme.harbor.api.generated.Product2Api
import com.acme.harbor.api.generated.model.MovementInputList
import com.acme.harbor.api.generated.model.PeerSimulationRequest
import com.acme.harbor.api.generated.model.PeerSimulationResult
import com.acme.harbor.api.generated.model.ProductOverview
import com.acme.harbor.api.generated.model.Projection
import com.acme.harbor.context.SessionContext
import com.acme.harbor.enums.TransportMode
import com.acme.harbor.manager.Product2Manager
import com.acme.harbor.mapper.ProjectionMapper
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import com.acme.harbor.api.generated.model.TransportMode as ApiTransportMode

/**
 * REST adapter for the `product2` tag (all session-scoped). Mappings are on the generated [Product2Api];
 * the session is read from `SessionContext.current()` bound by `SessionHeaderFilter`.
 */
@RestController
class Product2Controller(private val manager: Product2Manager) : Product2Api {

    override fun getProduct2Overview(xHarborSession: UUID, transportMode: ApiTransportMode?): ResponseEntity<ProductOverview> {
        val scope = SessionContext.current()
        val overview = manager.overview(scope, transportMode?.let { TransportMode.valueOf(it.name) })
        return ResponseEntity.ok(ProjectionMapper.overview(scope, overview))
    }

    override fun putProduct2Movements(xHarborSession: UUID, movementInputList: MovementInputList): ResponseEntity<Projection> {
        val scope = SessionContext.current()
        val tables = manager.replaceMovements(scope, ProjectionMapper.movementInputs(movementInputList))
        return ResponseEntity.ok(ProjectionMapper.projection(scope, tables))
    }

    override fun postProduct2PeerSimulation(xHarborSession: UUID, peerSimulationRequest: PeerSimulationRequest): ResponseEntity<PeerSimulationResult> {
        val scope = SessionContext.current()
        val result = manager.peerSimulation(scope, peerSimulationRequest.peerSegment, peerSimulationRequest.scalingFactor)
        return ResponseEntity.ok(ProjectionMapper.peerResult(result))
    }

    override fun getProduct2Projection(xHarborSession: UUID): ResponseEntity<Projection> {
        val scope = SessionContext.current()
        return ResponseEntity.ok(ProjectionMapper.projection(scope, manager.projection(scope)))
    }
}
