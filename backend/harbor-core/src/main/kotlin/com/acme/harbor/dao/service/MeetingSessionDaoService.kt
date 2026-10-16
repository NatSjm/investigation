package com.acme.harbor.dao.service

import com.acme.harbor.dao.model.MeetingSession
import com.acme.harbor.dao.repository.MeetingSessionRepository
import com.acme.harbor.dao.specification.MeetingSessionSpecifications
import com.acme.harbor.enums.SessionKind
import com.acme.harbor.enums.SessionStatus
import com.acme.harbor.exception.NotFoundException
import org.springframework.data.domain.Sort
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.util.UUID

/**
 * Persistence service over [MeetingSessionRepository]: the lookups every caller repeats (session by id or 404)
 * and the filtered listing built from [MeetingSessionSpecifications]. No business rules; those stay in
 * `manager/MeetingManager`.
 */
@Service
class MeetingSessionDaoService(private val repository: MeetingSessionRepository) {

    @Transactional(readOnly = true)
    fun find(sessionId: UUID): MeetingSession? = repository.findById(sessionId).orElse(null)

    @Transactional(readOnly = true)
    fun require(sessionId: UUID): MeetingSession = find(sessionId) ?: throw NotFoundException("Session", sessionId)

    /** Sessions matching the given filters (null = any), newest first. */
    @Transactional(readOnly = true)
    fun search(clientId: UUID?, status: SessionStatus?, kind: SessionKind?): List<MeetingSession> =
        repository.findAll(MeetingSessionSpecifications.matching(clientId, status, kind), Sort.by(Sort.Direction.DESC, "startedAt"))
}
