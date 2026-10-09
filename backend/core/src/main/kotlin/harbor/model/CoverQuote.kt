package harbor.model

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.Instant
import java.util.UUID

/** A quote obtained from cover-provider for the uncovered value of a session (table `cover_quote`, V6__cover.sql). */
@Entity
@Table(name = "cover_quote")
class CoverQuote(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "session_id", nullable = false)
    val sessionId: UUID,

    @Column(name = "requested_at", nullable = false)
    val requestedAt: Instant,

    @Column(name = "uncovered_value", nullable = false)
    val uncoveredValue: BigDecimal,

    @Column(name = "premium", nullable = false)
    val premium: BigDecimal,

    @Column(name = "provider_ref")
    val providerRef: String?,
)
