package harbor.event

import harbor.context.SessionContext
import harbor.enums.ProductGroup
import harbor.kafka.Topics
import harbor.kafka.events.MovementsLoadedEvent
import harbor.service.ProjectionService
import harbor.service.SessionScopeService
import org.slf4j.LoggerFactory
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component

/**
 * Consumes `harbor.imports.movements-loaded` and recomputes the stored projection of every OPEN Product 2
 * session of the affected clients (own consumer group, independent of the Product 1 listener).
 */
@Component
class Product2ProjectionRefreshListener(
    private val scopes: SessionScopeService,
    private val projectionService: ProjectionService,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    @KafkaListener(topics = [Topics.MOVEMENTS_LOADED], groupId = "harbor-product2")
    fun onMovementsLoaded(event: MovementsLoadedEvent) {
        var refreshed = 0
        event.clientIds.forEach { clientId ->
            scopes.openScopes(clientId, ProductGroup.PRODUCT2).forEach { scope ->
                SessionContext.withScope(scope) { projectionService.recompute(scope) }
                refreshed++
            }
        }
        log.info("Batch {}: refreshed {} open Product 2 session(s)", event.batchId, refreshed)
    }
}
