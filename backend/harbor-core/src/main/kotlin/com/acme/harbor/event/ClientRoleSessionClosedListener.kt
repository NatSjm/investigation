package com.acme.harbor.event

import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.enums.SessionKind
import com.acme.harbor.kafka.events.SessionClosed
import com.acme.harbor.service.ClientRoleService
import org.slf4j.LoggerFactory
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component
import java.util.UUID

/**
 * Consumes `harbor.meetings.session-closed`. When a CLIENT session was closed with a manual role override,
 * the override becomes the client's current role (`client_role`, source MANUAL). Overrides made in a
 * PREPARATION session are dry runs and are ignored.
 */
@Component
class ClientRoleSessionClosedListener(private val roleService: ClientRoleService) {

    private val log = LoggerFactory.getLogger(javaClass)

    @KafkaListener(topics = [TOPIC], groupId = "\${harbor.kafka.groups.clients}", autoStartup = "\${harbor.kafka.listeners.auto-startup:true}")
    fun onSessionClosed(event: SessionClosed) {
        val override = event.roleOverride ?: return
        if (SessionKind.valueOf(event.kind) != SessionKind.CLIENT) {
            log.debug("Ignoring role override from {} session {}", event.kind, event.sessionId)
            return
        }
        roleService.recordOverride(
            clientId = UUID.fromString(event.clientId),
            productGroup = ProductGroup.fromWire(event.productGroup),
            role = ClientRole.valueOf(override),
            reason = "Override set in meeting session ${event.sessionId}",
        )
    }

    companion object {
        /** Produced by [SessionEventsPublisher]; Avro schema `kafka-client/src/main/resources/avro/SessionClosed.avsc`. */
        const val TOPIC = "harbor.meetings.session-closed"
    }
}
