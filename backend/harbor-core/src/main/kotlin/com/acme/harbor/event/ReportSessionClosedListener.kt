package com.acme.harbor.event

import com.acme.harbor.kafka.events.SessionClosed
import com.acme.harbor.manager.ReportManager
import org.slf4j.LoggerFactory
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component
import java.util.UUID

/**
 * Consumes `harbor.meetings.session-closed`: every closed session (CLIENT and PREPARATION alike) gets a
 * report payload and a PDF render request.
 */
@Component
class ReportSessionClosedListener(private val reportManager: ReportManager) {

    private val log = LoggerFactory.getLogger(javaClass)

    @KafkaListener(topics = [TOPIC], groupId = "\${harbor.kafka.groups.reports}", autoStartup = "\${harbor.kafka.listeners.auto-startup:true}")
    fun onSessionClosed(event: SessionClosed) {
        log.info("Session {} closed ({}), building report", event.sessionId, event.kind)
        reportManager.createForClosedSession(UUID.fromString(event.sessionId))
    }

    companion object {
        /** Produced by [SessionEventsPublisher]; Avro schema `kafka-client/src/main/resources/avro/SessionClosed.avsc`. */
        const val TOPIC = "harbor.meetings.session-closed"
    }
}
