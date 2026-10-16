package com.acme.harbor.event

import com.acme.harbor.kafka.events.documentservice.ReportRendered
import com.acme.harbor.manager.ReportManager
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component

/** Consumes `harbor.reports.rendered` from document-service and records the PDF location on the report. */
@Component
class ReportRenderedListener(private val reportManager: ReportManager) {

    @KafkaListener(topics = [TOPIC], groupId = "\${harbor.kafka.groups.reports}", autoStartup = "\${harbor.kafka.listeners.auto-startup:true}")
    fun onReportRendered(event: ReportRendered) {
        reportManager.markRendered(event.sessionId, event.pdfPath)
    }

    companion object {
        /** Published by the external document-service; JSON schema `kafka-client/src/main/resources/json_document-service/ReportRendered.json`. */
        const val TOPIC = "harbor.reports.rendered"
    }
}
