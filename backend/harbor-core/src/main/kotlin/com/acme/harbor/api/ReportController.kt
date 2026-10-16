package com.acme.harbor.api

import com.acme.harbor.api.generated.ReportsApi
import com.acme.harbor.api.generated.model.ReportDto
import com.acme.harbor.manager.ReportManager
import com.acme.harbor.mapper.ReportMapper
import org.springframework.core.io.ByteArrayResource
import org.springframework.core.io.Resource
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID

/**
 * REST adapter for the `reports` tag. Keyed by session id in the path (reports are read after the session
 * is closed, so no `X-Harbor-Session` header is involved).
 */
@RestController
class ReportController(private val manager: ReportManager) : ReportsApi {

    override fun getReport(sessionId: UUID): ResponseEntity<ReportDto> =
        ResponseEntity.ok(ReportMapper.report(manager.get(sessionId)))

    override fun regenerateReport(sessionId: UUID): ResponseEntity<ReportDto> =
        ResponseEntity.status(HttpStatus.ACCEPTED).body(ReportMapper.report(manager.regenerate(sessionId)))

    override fun downloadReportPdf(sessionId: UUID): ResponseEntity<Resource> =
        ResponseEntity.ok()
            .headers(HttpHeadersFactory.pdfAttachment("meeting-report-$sessionId.pdf"))
            .body(ByteArrayResource(manager.downloadPdf(sessionId)))
}
