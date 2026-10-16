package com.acme.harbor.event

import com.acme.harbor.kafka.events.SessionClosed
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
        val event = SessionClosed(
            session.id.toString(),
            session.clientId.toString(),
            session.productGroup.wireValue,
            session.kind.name,
            session.roleOverride?.name,
        )
        producer.send(TOPIC, session.id.toString(), event)
        log.info("Published session-closed for session {} ({})", session.id, session.kind)
    }

    companion object {
        /** Consumed by ReportSessionClosedListener and ClientRoleSessionClosedListener; schema `kafka-client/src/main/resources/avro/SessionClosed.avsc`. */
        const val TOPIC = "harbor.meetings.session-closed"
    }
}
