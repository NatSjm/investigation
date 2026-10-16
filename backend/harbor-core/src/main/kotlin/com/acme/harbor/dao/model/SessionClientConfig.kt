package com.acme.harbor.dao.model

import com.acme.harbor.enums.CoverPreference
import com.acme.harbor.enums.PriceBasis
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.util.UUID

/**
 * Per-session client configuration (table `session_client_config`, V2__meetings.sql):
 * planning horizon, price basis (which side of the corridor prices are shown in) and cover preference.
 */
@Entity
@Table(name = "session_client_config")
class SessionClientConfig(
    @Id
    @Column(name = "session_id", nullable = false)
    val sessionId: UUID,

    @Column(name = "horizon_months", nullable = false)
    var horizonMonths: Int,

    @Enumerated(EnumType.STRING)
    @Column(name = "price_basis", nullable = false)
    var priceBasis: PriceBasis,

    @Enumerated(EnumType.STRING)
    @Column(name = "cover_preference", nullable = false)
    var coverPreference: CoverPreference = CoverPreference.NONE,
)
