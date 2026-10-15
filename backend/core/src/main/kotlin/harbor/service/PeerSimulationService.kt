package harbor.service

import harbor.context.SessionScope
import harbor.dao.MovementMonthlyDao
import harbor.dao.SessionPeerSimulationDao
import harbor.enums.ParameterKey
import harbor.model.SessionPeerSimulation
import harbor.utils.MonthGrid
import harbor.utils.PeerBenchmark
import harbor.utils.toPeriodDate
import harbor.utils.toYearMonth
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.Clock
import java.time.Instant
import java.time.LocalDate

/**
 * Peer simulation modal (modal 2, calculation `peer_benchmark_simulation`): median monthly quantity of the
 * peer segment over the last 12 full months scaled by `scalingFactor` (default parameter `peer.scaling_default`).
 * Each run is recorded in `session_peer_simulation`; the series is not stored.
 * @docs P1-003
 * @docs P2-003
 */
@Service
class PeerSimulationService(
    private val monthlyDao: MovementMonthlyDao,
    private val simulationDao: SessionPeerSimulationDao,
    private val parameters: ParameterService,
    private val clock: Clock,
) {

    data class Result(val simulation: SessionPeerSimulation, val series: List<PeerBenchmark.PeerPoint>)

    @Transactional
    fun simulate(scope: SessionScope, peerSegment: String, scalingFactor: BigDecimal?): Result {
        val factor = scalingFactor ?: parameters.required(ParameterKey.PEER_SCALING_DEFAULT)
        require(factor.signum() > 0) { "scalingFactor must be positive" }
        val months = MonthGrid.lastFullMonths(LocalDate.now(clock))
        val rows = monthlyDao.findAllBySegment(scope.productGroup, peerSegment, months.first().toPeriodDate(), months.last().toPeriodDate())

        // quantities per month and client, then the segment median per month
        val perMonth = months.associateWith { month ->
            rows.filter { it.period.toYearMonth() == month }
                .groupBy { it.clientId }
                .map { (_, clientRows) -> clientRows.fold(BigDecimal.ZERO) { acc, r -> acc + r.quantity } }
        }
        val simulation = simulationDao.save(
            SessionPeerSimulation(sessionId = scope.sessionId, peerSegment = peerSegment, scalingFactor = factor, generatedAt = Instant.now(clock)),
        )
        return Result(simulation, PeerBenchmark.simulate(perMonth, factor))
    }
}
