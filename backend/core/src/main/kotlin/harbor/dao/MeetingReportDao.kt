package harbor.dao

import harbor.model.MeetingReport
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Report payload and PDF location per closed session (table `meeting_report`). */
@Repository
interface MeetingReportDao : JpaRepository<MeetingReport, UUID>
