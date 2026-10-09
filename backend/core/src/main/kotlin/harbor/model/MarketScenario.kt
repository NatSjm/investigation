package harbor.model

import harbor.enums.ScenarioKind
import harbor.utils.ScenarioPricePath
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.time.Instant
import java.util.UUID

/**
 * A market scenario of a session (table `market_scenario`, V7__market_stress.sql): a named list of shocks
 * applied to the baseline curve by calculation `scenario_price_path`.
 */
@Entity
@Table(name = "market_scenario")
class MarketScenario(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "session_id", nullable = false)
    val sessionId: UUID,

    @Column(name = "name", nullable = false)
    var name: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "kind", nullable = false)
    var kind: ScenarioKind,

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "shocks", columnDefinition = "jsonb", nullable = false)
    var shocks: List<ScenarioShock> = emptyList(),

    @Column(name = "created_by", nullable = false)
    val createdBy: String,

    @Column(name = "created_at", nullable = false)
    val createdAt: Instant = Instant.now(),
) {
    fun calcShocks(): List<ScenarioPricePath.Shock> = shocks.map { it.toCalc() }
}
