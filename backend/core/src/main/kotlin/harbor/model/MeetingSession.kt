package harbor.model

import harbor.enums.ClientRole
import harbor.enums.ProductGroup
import harbor.enums.SessionKind
import harbor.enums.SessionStatus
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.time.Instant
import java.util.UUID

/**
 * A meeting session (table `meeting_session`, V2__meetings.sql + V9 `report_requested_at`).
 * `kind = CLIENT` is a real meeting, `PREPARATION` a dry run by the representative.
 * The parameter snapshot freezes the `parameter_set` values in force when the session was created so that
 * a report can be reproduced later.
 */
@Entity
@Table(name = "meeting_session")
class MeetingSession(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "client_id", nullable = false)
    val clientId: UUID,

    @Enumerated(EnumType.STRING)
    @Column(name = "product_group", nullable = false)
    val productGroup: ProductGroup,

    @Enumerated(EnumType.STRING)
    @Column(name = "kind", nullable = false)
    val kind: SessionKind,

    @Column(name = "representative_id", nullable = false)
    val representativeId: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    var status: SessionStatus = SessionStatus.OPEN,

    @Column(name = "started_at", nullable = false)
    val startedAt: Instant = Instant.now(),

    @Column(name = "closed_at")
    var closedAt: Instant? = null,

    @Enumerated(EnumType.STRING)
    @Column(name = "role_override")
    var roleOverride: ClientRole? = null,

    @Column(name = "role_override_reason")
    var roleOverrideReason: String? = null,

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "parameter_snapshot", columnDefinition = "jsonb")
    val parameterSnapshot: Map<String, BigDecimal> = emptyMap(),

    @Column(name = "report_requested_at")
    var reportRequestedAt: Instant? = null,
) {
    val isOpen: Boolean get() = status == SessionStatus.OPEN

    fun close(at: Instant) {
        check(isOpen) { "Session $id is already closed" }
        status = SessionStatus.CLOSED
        closedAt = at
    }
}
