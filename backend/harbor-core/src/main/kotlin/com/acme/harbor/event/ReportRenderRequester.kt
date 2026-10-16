package com.acme.harbor.event

import com.acme.harbor.component.ReportTemplateLoader
import com.acme.harbor.kafka.events.ReportRenderRequested
import org.springframework.beans.factory.annotation.Value
import com.acme.harbor.client.kafka.EventProducer
import org.springframework.stereotype.Component
import java.util.UUID

/**
 * Produces `harbor.reports.render-requested` (key = sessionId) for the external document-service.
 * The `payloadRef` is the URL under which document-service fetches the JSON payload (`getReport`); the
 * `template` is the meeting report HTML from [ReportTemplateLoader].
 */
@Component
class ReportRenderRequester(
    private val producer: EventProducer,
    private val templateLoader: ReportTemplateLoader,
    @Value("\${harbor.reports.payload-base-url}") private val payloadBaseUrl: String,
) {

    fun request(sessionId: UUID) {
        val event = ReportRenderRequested(
            sessionId.toString(),
            "$payloadBaseUrl/sessions/$sessionId/report",
            templateLoader.meetingReport(),
        )
        producer.send(TOPIC, sessionId.toString(), event)
    }

    companion object {
        /** Consumed by the external document-service; schema `kafka-client/src/main/resources/avro/ReportRenderRequested.avsc`. */
        const val TOPIC = "harbor.reports.render-requested"
    }
}
