package com.acme.harbor.event

import com.acme.harbor.kafka.Topics
import com.acme.harbor.kafka.events.ReportRendered
import com.acme.harbor.manager.ReportManager
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component

/** Consumes `harbor.reports.rendered` from document-service and records the PDF location on the report. */
@Component
class ReportRenderedListener(private val reportManager: ReportManager) {

    @KafkaListener(topics = [Topics.REPORT_RENDERED], groupId = "harbor-reports")
    fun onReportRendered(event: ReportRendered) {
        reportManager.markRendered(event.sessionId, event.pdfPath)
    }
}
