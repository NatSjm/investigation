package com.acme.harbor.dao.specification

import com.acme.harbor.dao.model.MeetingSession
import com.acme.harbor.enums.SessionKind
import com.acme.harbor.enums.SessionStatus
import org.springframework.data.jpa.domain.Specification
import java.util.UUID

/** JPA specifications of the session listing; a null argument means "no filter". Combined by `MeetingSessionDaoService`. */
object MeetingSessionSpecifications {

    fun ofClient(clientId: UUID?): Specification<MeetingSession> =
        Specification { root, _, cb -> clientId?.let { cb.equal(root.get<UUID>("clientId"), it) } }

    fun withStatus(status: SessionStatus?): Specification<MeetingSession> =
        Specification { root, _, cb -> status?.let { cb.equal(root.get<SessionStatus>("status"), it) } }

    fun ofKind(kind: SessionKind?): Specification<MeetingSession> =
        Specification { root, _, cb -> kind?.let { cb.equal(root.get<SessionKind>("kind"), it) } }

    fun matching(clientId: UUID?, status: SessionStatus?, kind: SessionKind?): Specification<MeetingSession> =
        Specification.allOf(ofClient(clientId), withStatus(status), ofKind(kind))
}
