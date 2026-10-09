package harbor.api

import harbor.api.generated.ReportsApi
import harbor.api.generated.model.Report
import harbor.manager.ReportManager
import harbor.mapper.ReportMapper
import org.springframework.core.io.ByteArrayResource
import org.springframework.core.io.Resource
import org.springframework.http.ContentDisposition
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID

/**
 * REST adapter for the `reports` tag. Keyed by session id in the path (reports are read after the session
 * is closed, so no `X-Harbor-Session` header is involved).
 */
@RestController
class ReportController(private val manager: ReportManager) : ReportsApi {

    override fun getReport(sessionId: UUID): ResponseEntity<Report> =
        ResponseEntity.ok(ReportMapper.report(manager.get(sessionId)))

    override fun regenerateReport(sessionId: UUID): ResponseEntity<Report> =
        ResponseEntity.status(HttpStatus.ACCEPTED).body(ReportMapper.report(manager.regenerate(sessionId)))

    override fun downloadReportPdf(sessionId: UUID): ResponseEntity<Resource> {
        val bytes = manager.downloadPdf(sessionId)
        val headers = HttpHeaders().apply {
            contentType = MediaType.APPLICATION_PDF
            contentDisposition = ContentDisposition.attachment().filename("meeting-report-$sessionId.pdf").build()
        }
        return ResponseEntity.ok().headers(headers).body(ByteArrayResource(bytes))
    }
}
