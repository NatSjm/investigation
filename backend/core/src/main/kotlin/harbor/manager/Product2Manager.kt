package harbor.manager

import harbor.context.SessionScope
import harbor.enums.ProductGroup
import harbor.enums.TransportMode
import harbor.exception.ValidationException
import harbor.service.ClientRoleService
import harbor.service.PeerSimulationService
import harbor.service.ProjectionInputAssembler
import harbor.service.ProjectionService
import harbor.service.ProjectionService.MovementInputCommand
import harbor.utils.ProjectionAggregator.Tables
import harbor.validator.MovementInputValidator
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

/**
 * Product 2 overview page of the current session: the four cumulative projection tables with transport mode
 * (ROAD / RAIL / SEA / AIR) as the breakdown dimension and an optional transport mode filter, the cover
 * ratio chart series, the movement modal and the peer simulation modal. Shares the projection pipeline,
 * DAOs and modals with Product 1.
 *
 * @docs P2-001
 */
@Service
class Product2Manager(
    private val projectionService: ProjectionService,
    private val assembler: ProjectionInputAssembler,
    private val peerSimulation: PeerSimulationService,
    private val roleService: ClientRoleService,
    private val movementValidator: MovementInputValidator,
) {

    @Transactional
    fun overview(scope: SessionScope, transportMode: TransportMode?): ProjectionService.Overview {
        requireProduct(scope)
        val tables = if (transportMode == null) {
            projectionService.loadOrCompute(scope)
        } else {
            projectionService.compute(scope) { it.transportMode == transportMode }
        }
        return projectionService.overview(scope, tables, role(scope), transportMode?.name)
    }

    @Transactional
    fun projection(scope: SessionScope): Tables = projectionService.loadOrCompute(requireProduct(scope))

    @Transactional
    fun replaceMovements(scope: SessionScope, inputs: List<MovementInputCommand>): Tables {
        requireProduct(scope)
        movementValidator.validate(scope.productGroup, assembler.grid(scope), inputs)
        return projectionService.replaceMovements(scope, inputs)
    }

    @Transactional
    fun peerSimulation(scope: SessionScope, peerSegment: String, scalingFactor: BigDecimal?): PeerSimulationService.Result =
        peerSimulation.simulate(requireProduct(scope), peerSegment, scalingFactor)

    private fun role(scope: SessionScope) = roleService.sessionRole(scope.clientId, scope.productGroup, scope.roleOverride)

    private fun requireProduct(scope: SessionScope): SessionScope = scope.also {
        ValidationException.check(it.productGroup == ProductGroup.PRODUCT2) { "Session ${it.sessionId} is not a Product 2 session" }
    }
}
