package harbor.service

import harbor.context.SessionScope
import harbor.dao.MeetingSessionDao
import harbor.dao.SessionClientConfigDao
import harbor.enums.ProductGroup
import harbor.enums.SessionStatus
import harbor.exception.NotFoundException
import harbor.model.MeetingSession
import org.springframework.stereotype.Service
import java.util.UUID

/**
 * Builds the [SessionScope] of a session. Used by `SessionHeaderFilter` for requests and by the Kafka
 * listeners that recompute projections of OPEN sessions outside a request.
 */
@Service
class SessionScopeService(
    private val sessionDao: MeetingSessionDao,
    private val configDao: SessionClientConfigDao,
) {

    fun resolve(session: MeetingSession): SessionScope {
        val config = configDao.findById(session.id).orElseThrow { NotFoundException("Session configuration", session.id) }
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
        resolve(sessionDao.findById(sessionId).orElseThrow { NotFoundException("Session", sessionId) })

    /** Scopes of all OPEN sessions of a client in a product group (projection refresh after an import). */
    fun openScopes(clientId: UUID, productGroup: ProductGroup): List<SessionScope> =
        sessionDao.findAllByClientIdAndProductGroupAndStatus(clientId, productGroup, SessionStatus.OPEN).map { resolve(it) }
}
