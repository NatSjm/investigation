package com.acme.harbor.service

import com.acme.harbor.context.SessionScope
import com.acme.harbor.dao.repository.MovementMonthlyRepository
import com.acme.harbor.dao.repository.SessionPeerSimulationRepository
import com.acme.harbor.enums.ParameterKey
import com.acme.harbor.dao.model.SessionPeerSimulation
import com.acme.harbor.utils.MonthGrid
import com.acme.harbor.utils.PeerBenchmark
import com.acme.harbor.utils.toPeriodDate
import com.acme.harbor.utils.toYearMonth
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
    private val monthlyRepository: MovementMonthlyRepository,
    private val simulationRepository: SessionPeerSimulationRepository,
    private val parameters: ParameterService,
    private val clock: Clock,
) {

    data class Result(val simulation: SessionPeerSimulation, val series: List<PeerBenchmark.PeerPoint>)

    @Transactional
    fun simulate(scope: SessionScope, peerSegment: String, scalingFactor: BigDecimal?): Result {
        val factor = scalingFactor ?: parameters.required(ParameterKey.PEER_SCALING_DEFAULT)
        require(factor.signum() > 0) { "scalingFactor must be positive" }
        val months = MonthGrid.lastFullMonths(LocalDate.now(clock))
        val rows = monthlyRepository.findAllBySegment(scope.productGroup, peerSegment, months.first().toPeriodDate(), months.last().toPeriodDate())

        // quantities per month and client, then the segment median per month
        val perMonth = months.associateWith { month ->
            rows.filter { it.period.toYearMonth() == month }
                .groupBy { it.clientId }
                .map { (_, clientRows) -> clientRows.fold(BigDecimal.ZERO) { acc, r -> acc + r.quantity } }
        }
        val simulation = simulationRepository.save(
            SessionPeerSimulation(sessionId = scope.sessionId, peerSegment = peerSegment, scalingFactor = factor, generatedAt = Instant.now(clock)),
        )
        return Result(simulation, PeerBenchmark.simulate(perMonth, factor))
    }
}
