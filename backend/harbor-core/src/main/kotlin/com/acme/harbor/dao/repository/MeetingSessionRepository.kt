package com.acme.harbor.dao.repository

import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.enums.SessionKind
import com.acme.harbor.enums.SessionStatus
import com.acme.harbor.dao.model.MeetingSession
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.JpaSpecificationExecutor
import org.springframework.stereotype.Repository
import java.util.UUID

/** Meeting sessions (table `meeting_session`). Filtered listing: `MeetingSessionSpecifications` via `MeetingSessionDaoService`. */
@Repository
interface MeetingSessionRepository : JpaRepository<MeetingSession, UUID>, JpaSpecificationExecutor<MeetingSession> {

    fun countByClientIdAndProductGroupAndStatus(clientId: UUID, productGroup: ProductGroup, status: SessionStatus): Int

    fun findAllByClientIdAndProductGroupAndStatus(clientId: UUID, productGroup: ProductGroup, status: SessionStatus): List<MeetingSession>
}
