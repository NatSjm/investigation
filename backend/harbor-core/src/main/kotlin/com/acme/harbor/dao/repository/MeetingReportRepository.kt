package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.MeetingReport
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Report payload and PDF location per closed session (table `meeting_report`). */
@Repository
interface MeetingReportRepository : JpaRepository<MeetingReport, UUID>
