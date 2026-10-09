package harbor.manager

import harbor.client.DocumentServiceClient
import harbor.dao.MeetingReportDao
import harbor.dao.MeetingSessionDao
import harbor.enums.ReportStatus
import harbor.event.ReportRenderRequester
import harbor.exception.NotFoundException
import harbor.model.MeetingReport
import harbor.service.ReportPayloadService
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.Clock
import java.time.Instant
import java.util.UUID

/**
 * Meeting report: builds the JSON payload from the projection tables, `stress_test_result` and the scenarios
 * of a session when it is closed ([ReportPayloadService]), stores it in `meeting_report`, asks document-service
 * for the PDF over Kafka (`harbor.reports.render-requested`, template `pdf/meeting-report.html`) and serves the
 * rendered PDF to the Meetings page.
 *
 * @docs RPT-001
 */
@Service
class ReportManager(
    private val reportDao: MeetingReportDao,
    private val sessionDao: MeetingSessionDao,
    private val payloadService: ReportPayloadService,
    private val renderRequester: ReportRenderRequester,
    private val documentService: DocumentServiceClient,
    private val clock: Clock,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    @Transactional(readOnly = true)
    fun get(sessionId: UUID): MeetingReport = reportDao.findById(sessionId).orElseThrow { NotFoundException("Report of session", sessionId) }

    /** Called by `ReportSessionClosedListener`: builds the payload and requests rendering. */
    @Transactional
    fun createForClosedSession(sessionId: UUID): MeetingReport {
        val report = reportDao.findById(sessionId).orElse(null)
            ?: MeetingReport(sessionId = sessionId, payload = emptyMap())
        report.payload = payloadService.build(sessionId)
        report.status = ReportStatus.PENDING
        reportDao.save(report)
        requestRender(report)
        return report
    }

    /** `POST /sessions/{id}/report`: rebuilds the payload and requests a fresh PDF, even for an old report. */
    @Transactional
    fun regenerate(sessionId: UUID): MeetingReport {
        val session = sessionDao.findById(sessionId).orElseThrow { NotFoundException("Session", sessionId) }
        check(!session.isOpen) { "Session $sessionId is still open; close it to produce a report" }
        return createForClosedSession(sessionId)
    }

    @Transactional
    fun markRendered(sessionId: UUID, pdfPath: String) {
        val report = get(sessionId)
        report.rendered(pdfPath, Instant.now(clock))
        log.info("Report of session {} rendered at {}", sessionId, pdfPath)
    }

    @Transactional(readOnly = true)
    fun downloadPdf(sessionId: UUID): ByteArray {
        val report = get(sessionId)
        val path = report.pdfPath
        check(report.status == ReportStatus.RENDERED && path != null) { "PDF of session $sessionId is not rendered yet" }
        return documentService.download(path)
    }

    private fun requestRender(report: MeetingReport) {
        renderRequester.request(report.sessionId)
        report.status = ReportStatus.REQUESTED
        sessionDao.findById(report.sessionId).ifPresent { it.reportRequestedAt = Instant.now(clock) }
    }
}
