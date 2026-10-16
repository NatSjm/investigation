package com.acme.harbor.exception

/** A session-scoped operation ran without a bound `SessionContext` (programming error) -> HTTP 500. */
class SessionNotBoundException : IllegalStateException("No meeting session is bound to the current request")
