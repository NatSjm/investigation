package com.acme.harbor.kafka.events

import java.util.UUID

/**
 * Payload of topic `Topics.REPORT_RENDER_REQUESTED`, consumed by the external document-service. Key: sessionId.
 *
 * @property payloadRef URL under which document-service fetches the JSON report payload (`getReport`)
 * @property template HTML template of the meeting report (core `pdf/meeting-report.html` with `pdf/report.css` inlined)
 */
data class ReportRenderRequested(
    val sessionId: UUID,
    val payloadRef: String,
    val template: String,
)
