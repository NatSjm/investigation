package com.acme.harbor.context

/**
 * Identity of the representative making the current request (author of sessions, scenarios and parameter
 * changes). The bean is defined in `WebConfig` from the forwarded user header; `system` outside a request.
 */
fun interface CurrentUser {
    fun id(): String

    companion object {
        /** Header set by the gateway after validating the bearer token. */
        const val HEADER = "X-Harbor-User"

        /** Identity used by jobs and Kafka listeners. */
        const val SYSTEM = "system"
    }
}
