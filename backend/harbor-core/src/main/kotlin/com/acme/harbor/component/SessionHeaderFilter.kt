package com.acme.harbor.component

import com.acme.harbor.HarborConstants
import com.acme.harbor.api.error.ProblemDetails
import com.acme.harbor.context.SessionContext
import com.acme.harbor.dao.service.MeetingSessionDaoService
import com.acme.harbor.exception.SessionClosedException
import com.acme.harbor.exception.SessionHeaderMissingException
import com.acme.harbor.service.SessionScopeService
import com.fasterxml.jackson.databind.ObjectMapper
import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter
import java.util.UUID

/**
 * Resolves the meeting session for every request under `/api/v1/session/` ([HarborConstants.SESSION_PATH_PREFIX])
 * from the `X-Harbor-Session` header (property `harbor.session.header`, default [HarborConstants.SESSION_HEADER])
 * and binds it to [SessionContext] for the duration of the request.
 *
 * - header missing          -> 428 Precondition Required
 * - unknown session id      -> 404 Not Found
 * - session already CLOSED  -> 409 Conflict
 *
 * Paths outside the session prefix (clients, sessions list, admin, ...) are not touched. The filter runs
 * before the MVC exception advice, so it writes the problem body itself ([ProblemDetails]).
 */
@Component
class SessionHeaderFilter(
    private val sessions: MeetingSessionDaoService,
    private val scopeService: SessionScopeService,
    private val objectMapper: ObjectMapper,
    @Value("\${harbor.session.header:" + HarborConstants.SESSION_HEADER + "}") private val headerName: String,
) : OncePerRequestFilter() {

    override fun shouldNotFilter(request: HttpServletRequest): Boolean =
        !request.requestURI.startsWith(HarborConstants.SESSION_PATH_PREFIX)

    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        val raw = request.getHeader(headerName)
        if (raw.isNullOrBlank()) {
            return reject(request, response, HttpStatus.PRECONDITION_REQUIRED, SessionHeaderMissingException(headerName, request.requestURI).message)
        }
        val sessionId = runCatching { UUID.fromString(raw.trim()) }.getOrNull()
            ?: return reject(request, response, HttpStatus.NOT_FOUND, "Session '$raw' is not a valid session id")
        val session = sessions.find(sessionId)
            ?: return reject(request, response, HttpStatus.NOT_FOUND, "Session $sessionId does not exist")
        if (!session.isOpen) {
            return reject(request, response, HttpStatus.CONFLICT, SessionClosedException(sessionId).message)
        }
        SessionContext.bind(scopeService.resolve(session))
        try {
            chain.doFilter(request, response)
        } finally {
            SessionContext.clear()
        }
    }

    private fun reject(request: HttpServletRequest, response: HttpServletResponse, status: HttpStatus, detail: String?) {
        response.status = status.value()
        response.contentType = MediaType.APPLICATION_PROBLEM_JSON_VALUE
        response.characterEncoding = Charsets.UTF_8.name()
        objectMapper.writeValue(response.writer, ProblemDetails.of(status, detail, request.requestURI))
    }
}
