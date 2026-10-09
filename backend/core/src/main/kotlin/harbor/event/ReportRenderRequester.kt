package harbor.event

import harbor.component.ReportTemplateLoader
import harbor.kafka.Topics
import harbor.kafka.events.ReportRenderRequested
import org.springframework.beans.factory.annotation.Value
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.stereotype.Component
import java.util.UUID

/**
 * Produces `harbor.reports.render-requested` (key = sessionId) for the external document-service.
 * The `payloadRef` is the URL under which document-service fetches the JSON payload (`getReport`); the
 * `template` is the meeting report HTML from [ReportTemplateLoader].
 */
@Component
class ReportRenderRequester(
    private val kafkaTemplate: KafkaTemplate<String, Any>,
    private val templateLoader: ReportTemplateLoader,
    @Value("\${harbor.reports.payload-base-url}") private val payloadBaseUrl: String,
) {

    fun request(sessionId: UUID) {
        val event = ReportRenderRequested(
            sessionId = sessionId,
            payloadRef = "$payloadBaseUrl/sessions/$sessionId/report",
            template = templateLoader.meetingReport(),
        )
        kafkaTemplate.send(Topics.REPORT_RENDER_REQUESTED, sessionId.toString(), event)
    }
}
