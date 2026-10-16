package com.acme.harbor.event

import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.enums.SessionKind
import com.acme.harbor.kafka.Topics
import com.acme.harbor.kafka.events.SessionClosedEvent
import com.acme.harbor.service.ClientRoleService
import org.slf4j.LoggerFactory
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component

/**
 * Consumes `harbor.meetings.session-closed`. When a CLIENT session was closed with a manual role override,
 * the override becomes the client's current role (`client_role`, source MANUAL). Overrides made in a
 * PREPARATION session are dry runs and are ignored.
 */
@Component
class ClientRoleSessionClosedListener(private val roleService: ClientRoleService) {

    private val log = LoggerFactory.getLogger(javaClass)

    @KafkaListener(topics = [Topics.SESSION_CLOSED], groupId = "harbor-clients")
    fun onSessionClosed(event: SessionClosedEvent) {
        val override = event.roleOverride ?: return
        if (SessionKind.valueOf(event.kind) != SessionKind.CLIENT) {
            log.debug("Ignoring role override from {} session {}", event.kind, event.sessionId)
            return
        }
        roleService.recordOverride(
            clientId = event.clientId,
            productGroup = ProductGroup.fromWire(event.productGroup),
            role = ClientRole.valueOf(override),
            reason = "Override set in meeting session ${event.sessionId}",
        )
    }
}
