package com.acme.harbor.event

import com.acme.harbor.kafka.Topics
import com.acme.harbor.kafka.events.SessionClosedEvent
import com.acme.harbor.dao.model.MeetingSession
import org.slf4j.LoggerFactory
import com.acme.harbor.client.kafka.EventProducer
import org.springframework.stereotype.Component

/**
 * Produces `harbor.meetings.session-closed` (key = sessionId) when a session is closed.
 * Consumers: ReportSessionClosedListener (report payload + PDF) and ClientRoleSessionClosedListener (role override).
 */
@Component
class SessionEventsPublisher(private val producer: EventProducer) {

    private val log = LoggerFactory.getLogger(javaClass)

    fun sessionClosed(session: MeetingSession) {
        val event = SessionClosedEvent(
            sessionId = session.id,
            clientId = session.clientId,
            productGroup = session.productGroup.wireValue,
            kind = session.kind.name,
            roleOverride = session.roleOverride?.name,
        )
        producer.send(Topics.SESSION_CLOSED, session.id.toString(), event)
        log.info("Published session-closed for session {} ({})", session.id, session.kind)
    }
}
