package harbor.manager

import harbor.context.SessionScope
import harbor.enums.ProductGroup
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
 * Product 1 overview page of the current session: the four cumulative projection tables (by sub-product,
 * by city hub, by direction, summary) with an optional city filter, the cover ratio chart series, the
 * movement modal (modelled movements per month) and the peer simulation modal.
 *
 * All operations are scoped by the session the controller reads from `SessionContext.current()` (header `X-Harbor-Session`).
 *
 * @docs P1-001
 */
@Service
class Product1Manager(
    private val projectionService: ProjectionService,
    private val assembler: ProjectionInputAssembler,
    private val peerSimulation: PeerSimulationService,
    private val roleService: ClientRoleService,
    private val movementValidator: MovementInputValidator,
) {

    @Transactional
    fun overview(scope: SessionScope, city: String?): ProjectionService.Overview {
        requireProduct(scope)
        city?.let { ValidationException.check(it in ProductGroup.PRODUCT1_CITIES) { "Unknown city hub '$it'" } }
        val tables = if (city == null) projectionService.loadOrCompute(scope) else projectionService.compute(scope) { it.city == city }
        return projectionService.overview(scope, tables, role(scope), city)
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
        ValidationException.check(it.productGroup == ProductGroup.PRODUCT1) { "Session ${it.sessionId} is not a Product 1 session" }
    }
}
