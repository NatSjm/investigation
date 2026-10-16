package com.acme.harbor.event

import com.acme.harbor.context.SessionContext
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.kafka.events.MovementsLoaded
import com.acme.harbor.service.ProjectionService
import com.acme.harbor.service.SessionScopeService
import org.slf4j.LoggerFactory
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component
import java.util.UUID

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

    @KafkaListener(topics = [TOPIC], groupId = "\${harbor.kafka.groups.product2}", autoStartup = "\${harbor.kafka.listeners.auto-startup:true}")
    fun onMovementsLoaded(event: MovementsLoaded) {
        var refreshed = 0
        event.clientIds.forEach { clientId ->
            scopes.openScopes(UUID.fromString(clientId), ProductGroup.PRODUCT2).forEach { scope ->
                SessionContext.withScope(scope) { projectionService.recompute(scope) }
                refreshed++
            }
        }
        log.info("Batch {}: refreshed {} open Product 2 session(s)", event.batchId, refreshed)
    }

    companion object {
        /** Produced by [MovementsLoadedPublisher]; Avro schema `kafka-client/src/main/resources/avro/MovementsLoaded.avsc`. */
        const val TOPIC = "harbor.imports.movements-loaded"
    }
}
