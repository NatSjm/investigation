package harbor.model

import harbor.enums.ReportStatus
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.time.Instant
import java.util.UUID

/**
 * The report of a meeting session (table `meeting_report`, V8__reports.sql): the JSON payload built when
 * the session was closed, and the location of the PDF rendered by document-service.
 */
@Entity
@Table(name = "meeting_report")
class MeetingReport(
    @Id
    @Column(name = "session_id", nullable = false)
    val sessionId: UUID,

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "payload", columnDefinition = "jsonb", nullable = false)
    var payload: Map<String, Any?>,

    @Column(name = "pdf_path")
    var pdfPath: String? = null,

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    var status: ReportStatus = ReportStatus.PENDING,

    @Column(name = "rendered_at")
    var renderedAt: Instant? = null,
) {
    fun rendered(path: String, at: Instant) {
        pdfPath = path
        renderedAt = at
        status = ReportStatus.RENDERED
    }
}
