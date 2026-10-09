package harbor.api

import harbor.api.generated.MeetingsApi
import harbor.api.generated.model.CreateSessionRequest
import harbor.api.generated.model.RoleOverrideRequest
import harbor.api.generated.model.Session
import harbor.api.generated.model.SessionCreated
import harbor.manager.MeetingManager
import harbor.mapper.SessionMapper
import harbor.mapper.SessionMapper.toDomain
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import harbor.api.generated.model.SessionKind as ApiSessionKind
import harbor.api.generated.model.SessionStatus as ApiSessionStatus

/**
 * REST adapter for the `meetings` tag. Mappings are on the generated [MeetingsApi] interface.
 * These endpoints take the session id from the path, not from the `X-Harbor-Session` header.
 */
@RestController
class SessionController(private val manager: MeetingManager) : MeetingsApi {

    override fun createSession(clientId: UUID, createSessionRequest: CreateSessionRequest): ResponseEntity<SessionCreated> {
        val view = manager.create(
            clientId = clientId,
            productGroup = createSessionRequest.productGroup.toDomain(),
            kind = createSessionRequest.kind.toDomain(),
            horizonMonths = createSessionRequest.horizonMonths,
        )
        return ResponseEntity.status(HttpStatus.CREATED).body(SessionMapper.created(view))
    }

    override fun listSessions(clientId: UUID?, status: ApiSessionStatus?, kind: ApiSessionKind?): ResponseEntity<List<Session>> =
        ResponseEntity.ok(manager.list(clientId, status?.toDomain(), kind?.toDomain()).map(SessionMapper::session))

    override fun getSession(sessionId: UUID): ResponseEntity<Session> =
        ResponseEntity.ok(SessionMapper.session(manager.get(sessionId)))

    override fun closeSession(sessionId: UUID): ResponseEntity<Session> =
        ResponseEntity.ok(SessionMapper.session(manager.close(sessionId)))

    override fun setRoleOverride(sessionId: UUID, roleOverrideRequest: RoleOverrideRequest): ResponseEntity<Session> =
        ResponseEntity.ok(
            SessionMapper.session(manager.setRoleOverride(sessionId, roleOverrideRequest.role.toDomain(), roleOverrideRequest.reason)),
        )
}
