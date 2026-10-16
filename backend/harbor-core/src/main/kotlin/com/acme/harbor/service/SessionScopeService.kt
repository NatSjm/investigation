package com.acme.harbor.service

import com.acme.harbor.context.SessionScope
import com.acme.harbor.dao.repository.MeetingSessionRepository
import com.acme.harbor.dao.service.MeetingSessionDaoService
import com.acme.harbor.dao.repository.SessionClientConfigRepository
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.enums.SessionStatus
import com.acme.harbor.exception.NotFoundException
import com.acme.harbor.dao.model.MeetingSession
import org.springframework.stereotype.Service
import java.util.UUID

/**
 * Builds the [SessionScope] of a session. Used by `SessionHeaderFilter` for requests and by the Kafka
 * listeners that recompute projections of OPEN sessions outside a request.
 */
@Service
class SessionScopeService(
    private val sessionRepository: MeetingSessionRepository,
    private val sessionDaoService: MeetingSessionDaoService,
    private val configRepository: SessionClientConfigRepository,
) {

    fun resolve(session: MeetingSession): SessionScope {
        val config = configRepository.findById(session.id).orElseThrow { NotFoundException("Session configuration", session.id) }
        return SessionScope(
            sessionId = session.id,
            clientId = session.clientId,
            productGroup = session.productGroup,
            kind = session.kind,
            horizonMonths = config.horizonMonths,
            priceBasis = config.priceBasis,
            representativeId = session.representativeId,
            roleOverride = session.roleOverride,
        )
    }

    fun resolve(sessionId: UUID): SessionScope =
        resolve(sessionDaoService.require(sessionId))

    /** Scopes of all OPEN sessions of a client in a product group (projection refresh after an import). */
    fun openScopes(clientId: UUID, productGroup: ProductGroup): List<SessionScope> =
        sessionRepository.findAllByClientIdAndProductGroupAndStatus(clientId, productGroup, SessionStatus.OPEN).map { resolve(it) }
}
