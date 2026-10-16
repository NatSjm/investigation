package com.acme.harbor.context

import com.acme.harbor.exception.SessionNotBoundException

/**
 * Thread-bound holder of the current [SessionScope].
 *
 * Session-scoped controllers and managers call [current]; nobody reads the header themselves.
 * Throws [SessionNotBoundException] when a session-scoped operation is invoked outside a session request
 * (programming error, surfaces as HTTP 500 rather than silently using a wrong session).
 */
object SessionContext {
    private val holder = ThreadLocal<SessionScope?>()

    fun current(): SessionScope = holder.get() ?: throw SessionNotBoundException()

    fun currentOrNull(): SessionScope? = holder.get()

    fun bind(scope: SessionScope) = holder.set(scope)

    fun clear() = holder.remove()

    /** Runs [block] with [scope] bound, restoring the previous scope afterwards (used by listeners and jobs). */
    fun <T> withScope(scope: SessionScope, block: () -> T): T {
        val previous = holder.get()
        holder.set(scope)
        try {
            return block()
        } finally {
            if (previous == null) holder.remove() else holder.set(previous)
        }
    }
}
