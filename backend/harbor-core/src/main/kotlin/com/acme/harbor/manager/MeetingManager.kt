package com.acme.harbor.manager

import com.acme.harbor.context.CurrentUser
import com.acme.harbor.dao.repository.MeetingSessionRepository
import com.acme.harbor.dao.service.MeetingSessionDaoService
import com.acme.harbor.dao.repository.SessionClientConfigRepository
import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.ParameterKey
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.enums.SessionKind
import com.acme.harbor.enums.SessionStatus
import com.acme.harbor.event.SessionEventsPublisher
import com.acme.harbor.exception.NotFoundException
import com.acme.harbor.exception.SessionClosedException
import com.acme.harbor.exception.ValidationException
import com.acme.harbor.dao.model.MeetingSession
import com.acme.harbor.dao.model.SessionClientConfig
import com.acme.harbor.service.ClientProfileService
import com.acme.harbor.service.ParameterService
import com.acme.harbor.utils.MonthGrid
import com.acme.harbor.validator.RoleOverrideValidator
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.Clock
import java.time.Instant
import java.util.UUID

/**
 * Meeting session lifecycle: create (CLIENT or PREPARATION), list, read, manual role override and close.
 *
 * Creating a session freezes a snapshot of the relevant `parameter_set` values; closing it emits
 * `harbor.meetings.session-closed`, which triggers the report and the role override propagation.
 * Session-scoped endpoints (`/session` sub-paths) rely on `SessionHeaderFilter` and `SessionContext`, not on this manager.
 *
 * @docs SES-001
 */
@Service
class MeetingManager(
    private val sessionRepository: MeetingSessionRepository,
    private val sessionDaoService: MeetingSessionDaoService,
    private val configRepository: SessionClientConfigRepository,
    private val clientProfiles: ClientProfileService,
    private val parameters: ParameterService,
    private val roleOverrideValidator: RoleOverrideValidator,
    private val events: SessionEventsPublisher,
    private val currentUser: CurrentUser,
    private val clock: Clock,
) {

    data class SessionView(val session: MeetingSession, val config: SessionClientConfig, val clientName: String)

    @Transactional
    fun create(clientId: UUID, productGroup: ProductGroup, kind: SessionKind, horizonMonths: Int?): SessionView {
        val client = clientProfiles.get(clientId)
        val horizon = horizonMonths ?: parameters.required(ParameterKey.PROJECTION_HORIZON_MONTHS_DEFAULT).toInt()
        ValidationException.check(horizon in MonthGrid.MIN_HORIZON..MonthGrid.MAX_HORIZON) { "horizonMonths out of range: $horizon" }

        val session = sessionRepository.save(
            MeetingSession(
                clientId = clientId,
                productGroup = productGroup,
                kind = kind,
                representativeId = currentUser.id(),
                startedAt = Instant.now(clock),
                parameterSnapshot = snapshot(productGroup),
            ),
        )
        val config = configRepository.save(
            SessionClientConfig(sessionId = session.id, horizonMonths = horizon, priceBasis = productGroup.priceBases.first()),
        )
        return SessionView(session, config, client.name)
    }

    @Transactional(readOnly = true)
    fun list(clientId: UUID?, status: SessionStatus?, kind: SessionKind?): List<SessionView> =
        sessionDaoService.search(clientId, status, kind).map { view(it) }

    @Transactional(readOnly = true)
    fun get(sessionId: UUID): SessionView = view(load(sessionId))

    @Transactional
    fun setRoleOverride(sessionId: UUID, role: ClientRole, reason: String): SessionView {
        val session = load(sessionId)
        roleOverrideValidator.validate(session, role, reason)
        session.roleOverride = role
        session.roleOverrideReason = reason.trim()
        return view(session)
    }

    @Transactional
    fun close(sessionId: UUID): SessionView {
        val session = load(sessionId)
        if (!session.isOpen) throw SessionClosedException(sessionId)
        session.close(Instant.now(clock))
        events.sessionClosed(session)
        return view(session)
    }

    private fun load(sessionId: UUID): MeetingSession =
        sessionDaoService.require(sessionId)

    private fun view(session: MeetingSession): SessionView = SessionView(
        session = session,
        config = configRepository.findById(session.id).orElseThrow { NotFoundException("Session configuration", session.id) },
        clientName = clientProfiles.get(session.clientId).name,
    )

    private fun snapshot(productGroup: ProductGroup): Map<String, BigDecimal> = buildMap {
        listOf(
            ParameterKey.ROLE_MIN_VOLUME,
            ParameterKey.ROLE_IMPORTER_THRESHOLD,
            ParameterKey.ROLE_EXPORTER_THRESHOLD,
            ParameterKey.COVER_DEFAULT_PREMIUM_RATE,
            ParameterKey.PEER_SCALING_DEFAULT,
            ParameterKey.STRESS_ROUNDING_SCALE,
        ).forEach { key -> parameters.find(key)?.let { put(key.key, it) } }
        productGroup.priceBases.forEach { basis ->
            parameters.find(ParameterKey.TARIFF_RATE, productGroup, basis.name)?.let { put("${ParameterKey.TARIFF_RATE.key}.${basis.name}", it) }
        }
    }
}
