package harbor.model

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

/**
 * One month of the stress test of a scenario for one dimension value (table `stress_test_result`,
 * V7__market_stress.sql). Output of calculation `stress_test_monthly`; replaced on every run.
 */
@Entity
@Table(name = "stress_test_result")
class StressTestResult(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    val id: Long? = null,

    @Column(name = "session_id", nullable = false)
    val sessionId: UUID,

    @Column(name = "scenario_id", nullable = false)
    val scenarioId: UUID,

    @Column(name = "period", nullable = false)
    val period: LocalDate,

    @Column(name = "dimension_value", nullable = false)
    val dimensionValue: String,

    @Column(name = "exposure", nullable = false)
    val exposure: BigDecimal,

    @Column(name = "transport_cost_delta", nullable = false)
    val transportCostDelta: BigDecimal,

    @Column(name = "cumulative_exposure", nullable = false)
    val cumulativeExposure: BigDecimal,
)
