package harbor.kafka.events

import java.util.UUID

/** Payload of topic `Topics.REPORT_RENDERED`, published by the external document-service. Key: sessionId. */
data class ReportRendered(
    val sessionId: UUID,
    val pdfPath: String,
)
