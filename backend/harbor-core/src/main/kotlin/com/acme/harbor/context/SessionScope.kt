package com.acme.harbor.context

import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.PriceBasis
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.enums.SessionKind
import java.util.UUID

/**
 * The meeting session a request is scoped to. Built by `SessionScopeService` and bound to [SessionContext]
 * by `SessionHeaderFilter` from the `X-Harbor-Session` header for every `/api/v1/session` sub-path request.
 */
data class SessionScope(
    val sessionId: UUID,
    val clientId: UUID,
    val productGroup: ProductGroup,
    val kind: SessionKind,
    val horizonMonths: Int,
    /** Price basis chosen for the session (`session_client_config.price_basis`). */
    val priceBasis: PriceBasis,
    val representativeId: String,
    /** Manual role override set during the meeting, null when the algorithm result applies. */
    val roleOverride: ClientRole? = null,
)
