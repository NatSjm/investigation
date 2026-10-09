package harbor.mapper

import harbor.api.generated.model.Report
import harbor.enums.ReportStatus
import harbor.model.MeetingReport
import java.time.ZoneOffset

/** Maps the meeting report entity to the generated API model. */
object ReportMapper {

    fun report(r: MeetingReport) = Report(
        sessionId = r.sessionId,
        status = Report.Status.valueOf(r.status.name),
        payload = r.payload,
        pdfAvailable = r.status == ReportStatus.RENDERED && r.pdfPath != null,
        renderedAt = r.renderedAt?.atOffset(ZoneOffset.UTC),
    )
}
