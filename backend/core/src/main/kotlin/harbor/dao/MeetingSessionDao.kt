package harbor.dao

import harbor.enums.ProductGroup
import harbor.enums.SessionKind
import harbor.enums.SessionStatus
import harbor.model.MeetingSession
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.util.UUID

/** Meeting sessions (table `meeting_session`). */
@Repository
interface MeetingSessionDao : JpaRepository<MeetingSession, UUID> {

    @Query(
        """
        select s from MeetingSession s
        where (:clientId is null or s.clientId = :clientId)
          and (:status is null or s.status = :status)
          and (:kind is null or s.kind = :kind)
        order by s.startedAt desc
        """,
    )
    fun search(clientId: UUID?, status: SessionStatus?, kind: SessionKind?): List<MeetingSession>

    fun countByClientIdAndProductGroupAndStatus(clientId: UUID, productGroup: ProductGroup, status: SessionStatus): Int

    fun findAllByClientIdAndProductGroupAndStatus(clientId: UUID, productGroup: ProductGroup, status: SessionStatus): List<MeetingSession>
}
