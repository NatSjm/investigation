package harbor.event

import harbor.kafka.Topics
import harbor.kafka.events.SessionClosedEvent
import harbor.model.MeetingSession
import org.slf4j.LoggerFactory
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.stereotype.Component

/**
 * Produces `harbor.meetings.session-closed` (key = sessionId) when a session is closed.
 * Consumers: ReportSessionClosedListener (report payload + PDF) and ClientRoleSessionClosedListener (role override).
 */
@Component
class SessionEventsPublisher(private val kafkaTemplate: KafkaTemplate<String, Any>) {

    private val log = LoggerFactory.getLogger(javaClass)

    fun sessionClosed(session: MeetingSession) {
        val event = SessionClosedEvent(
            sessionId = session.id,
            clientId = session.clientId,
            productGroup = session.productGroup.wireValue,
            kind = session.kind.name,
            roleOverride = session.roleOverride?.name,
        )
        kafkaTemplate.send(Topics.SESSION_CLOSED, session.id.toString(), event)
        log.info("Published session-closed for session {} ({})", session.id, session.kind)
    }
}
