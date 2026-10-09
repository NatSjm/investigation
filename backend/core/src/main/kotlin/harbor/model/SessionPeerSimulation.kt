package harbor.model

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.Instant
import java.util.UUID

/**
 * One run of the peer simulation modal (table `session_peer_simulation`, V4__session_inputs.sql).
 * The series itself is recomputed on demand from `movement_monthly` (calculation `peer_benchmark_simulation`).
 */
@Entity
@Table(name = "session_peer_simulation")
class SessionPeerSimulation(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "session_id", nullable = false)
    val sessionId: UUID,

    @Column(name = "peer_segment", nullable = false)
    val peerSegment: String,

    @Column(name = "scaling_factor", nullable = false)
    val scalingFactor: BigDecimal,

    @Column(name = "generated_at", nullable = false)
    val generatedAt: Instant,
)
