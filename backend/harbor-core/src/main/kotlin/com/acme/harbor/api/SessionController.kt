package com.acme.harbor.api

import com.acme.harbor.api.generated.MeetingsApi
import com.acme.harbor.api.generated.model.CreateSessionRequestDto
import com.acme.harbor.api.generated.model.RoleOverrideRequestDto
import com.acme.harbor.api.generated.model.SessionDto
import com.acme.harbor.api.generated.model.SessionCreatedDto
import com.acme.harbor.manager.MeetingManager
import com.acme.harbor.mapper.SessionMapper
import com.acme.harbor.mapper.SessionMapper.toDomain
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import com.acme.harbor.api.generated.model.SessionKindDto as ApiSessionKind
import com.acme.harbor.api.generated.model.SessionStatusDto as ApiSessionStatus
/**
 * REST adapter for the `meetings` tag. Mappings are on the generated [MeetingsApi] interface.
 * These endpoints take the session id from the path, not from the `X-Harbor-SessionDto` header.
 */
@RestController
class SessionController(private val manager: MeetingManager) : MeetingsApi {

    override fun createSession(clientId: UUID, createSessionRequest: CreateSessionRequestDto): ResponseEntity<SessionCreatedDto> {
        val view = manager.create(
            clientId = clientId,
            productGroup = createSessionRequest.productGroup.toDomain(),
            kind = createSessionRequest.kind.toDomain(),
            horizonMonths = createSessionRequest.horizonMonths,
        )
        return ResponseEntity.status(HttpStatus.CREATED).body(SessionMapper.created(view))
    }

    override fun listSessions(clientId: UUID?, status: ApiSessionStatus?, kind: ApiSessionKind?): ResponseEntity<List<SessionDto>> =
        ResponseEntity.ok(manager.list(clientId, status?.toDomain(), kind?.toDomain()).map(SessionMapper::session))

    override fun getSession(sessionId: UUID): ResponseEntity<SessionDto> =
        ResponseEntity.ok(SessionMapper.session(manager.get(sessionId)))

    override fun closeSession(sessionId: UUID): ResponseEntity<SessionDto> =
        ResponseEntity.ok(SessionMapper.session(manager.close(sessionId)))

    override fun setRoleOverride(sessionId: UUID, roleOverrideRequest: RoleOverrideRequestDto): ResponseEntity<SessionDto> =
        ResponseEntity.ok(
            SessionMapper.session(manager.setRoleOverride(sessionId, roleOverrideRequest.role.toDomain(), roleOverrideRequest.reason)),
        )
}
