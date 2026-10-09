package harbor.api

import harbor.api.generated.Product2Api
import harbor.api.generated.model.MovementInputList
import harbor.api.generated.model.PeerSimulationRequest
import harbor.api.generated.model.PeerSimulationResult
import harbor.api.generated.model.ProductOverview
import harbor.api.generated.model.Projection
import harbor.context.SessionContext
import harbor.enums.TransportMode
import harbor.manager.Product2Manager
import harbor.mapper.ProjectionMapper
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import harbor.api.generated.model.TransportMode as ApiTransportMode

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
