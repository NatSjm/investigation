package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.ReportDto
import com.acme.harbor.enums.ReportStatus
import com.acme.harbor.dao.model.MeetingReport
import java.time.ZoneOffset

/** Maps the meeting report entity to the generated API model. */
object ReportMapper {

    @Suppress("UNCHECKED_CAST")
    fun report(r: MeetingReport) = ReportDto(
        sessionId = r.sessionId,
        status = ReportDto.Status.valueOf(r.status.name),
        payload = r.payload as Map<String, Any>,
        pdfAvailable = r.status == ReportStatus.RENDERED && r.pdfPath != null,
        renderedAt = r.renderedAt?.atOffset(ZoneOffset.UTC),
    )
}
