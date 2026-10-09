package harbor.exception

import java.util.UUID

/** The meeting session is already CLOSED and cannot be changed or used for `/session/**` requests -> HTTP 409. */
class SessionClosedException(sessionId: UUID) : RuntimeException("Session $sessionId is closed")
