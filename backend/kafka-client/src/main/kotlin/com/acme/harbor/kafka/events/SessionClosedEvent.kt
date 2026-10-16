package com.acme.harbor.kafka.events

import java.util.UUID

/**
 * Payload of topic `Topics.SESSION_CLOSED`. Key: sessionId.
 *
 * @property productGroup wire value of the product group (`product1` / `product2`)
 * @property kind `CLIENT` (real meeting) or `PREPARATION` (dry run)
 * @property roleOverride `IMPORTER` / `EXPORTER` / `MIXED` when a manual override was set in the session, else null
 */
data class SessionClosedEvent(
    val sessionId: UUID,
    val clientId: UUID,
    val productGroup: String,
    val kind: String,
    val roleOverride: String? = null,
)
