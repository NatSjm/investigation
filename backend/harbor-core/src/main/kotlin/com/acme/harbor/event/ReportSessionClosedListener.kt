package com.acme.harbor.event

import com.acme.harbor.kafka.Topics
import com.acme.harbor.kafka.events.SessionClosedEvent
import com.acme.harbor.manager.ReportManager
import org.slf4j.LoggerFactory
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component

/**
 * Consumes `harbor.meetings.session-closed`: every closed session (CLIENT and PREPARATION alike) gets a
 * report payload and a PDF render request.
 */
@Component
class ReportSessionClosedListener(private val reportManager: ReportManager) {

    private val log = LoggerFactory.getLogger(javaClass)

    @KafkaListener(topics = [Topics.SESSION_CLOSED], groupId = "harbor-reports")
    fun onSessionClosed(event: SessionClosedEvent) {
        log.info("Session {} closed ({}), building report", event.sessionId, event.kind)
        reportManager.createForClosedSession(event.sessionId)
    }
}
