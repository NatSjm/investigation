package harbor.component

import com.fasterxml.jackson.databind.ObjectMapper
import harbor.context.SessionContext
import harbor.dao.MeetingSessionDao
import harbor.exception.SessionClosedException
import harbor.exception.SessionHeaderMissingException
import harbor.service.SessionScopeService
import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.http.ProblemDetail
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter
import java.util.UUID

/**
 * Resolves the meeting session for every request under `/api/v1/session/` from the `X-Harbor-Session`
 * header (property `harbor.session.header`) and binds it to [SessionContext] for the duration of the request.
 *
 * - header missing          -> 428 Precondition Required
 * - unknown session id      -> 404 Not Found
 * - session already CLOSED  -> 409 Conflict
 *
 * Paths outside `/api/v1/session/` (clients, sessions list, admin, ...) are not touched. The filter runs
 * before the MVC exception advice, so it writes the problem body itself.
 */
@Component
class SessionHeaderFilter(
    private val sessionDao: MeetingSessionDao,
    private val scopeService: SessionScopeService,
    private val objectMapper: ObjectMapper,
    @Value("\${harbor.session.header:X-Harbor-Session}") private val headerName: String,
) : OncePerRequestFilter() {

    override fun shouldNotFilter(request: HttpServletRequest): Boolean =
        !request.requestURI.startsWith(SESSION_PATH_PREFIX)

    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        val raw = request.getHeader(headerName)
        if (raw.isNullOrBlank()) {
            return reject(response, HttpStatus.PRECONDITION_REQUIRED, SessionHeaderMissingException(headerName, request.requestURI).message)
        }
        val sessionId = runCatching { UUID.fromString(raw.trim()) }.getOrNull()
            ?: return reject(response, HttpStatus.NOT_FOUND, "Session '$raw' is not a valid session id")
        val session = sessionDao.findById(sessionId).orElse(null)
            ?: return reject(response, HttpStatus.NOT_FOUND, "Session $sessionId does not exist")
        if (!session.isOpen) {
            return reject(response, HttpStatus.CONFLICT, SessionClosedException(sessionId).message)
        }
        SessionContext.bind(scopeService.resolve(session))
        try {
            chain.doFilter(request, response)
        } finally {
            SessionContext.clear()
        }
    }

    private fun reject(response: HttpServletResponse, status: HttpStatus, detail: String?) {
        val problem = ProblemDetail.forStatusAndDetail(status, detail ?: status.reasonPhrase).apply { title = status.reasonPhrase }
        response.status = status.value()
        response.contentType = MediaType.APPLICATION_PROBLEM_JSON_VALUE
        response.characterEncoding = Charsets.UTF_8.name()
        objectMapper.writeValue(response.writer, problem)
    }

    companion object {
        const val SESSION_PATH_PREFIX = "/api/v1/session/"
    }
}
