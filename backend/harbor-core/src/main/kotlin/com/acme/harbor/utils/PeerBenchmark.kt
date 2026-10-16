package com.acme.harbor.utils

import java.math.BigDecimal
import java.time.YearMonth

/**
 * Peer benchmark simulation (modal 2 on the product pages): models the movements of similar products
 * at peer firms of the same segment.
 *
 * Current definition: `peerQty(m) = segmentMedianQty(m) * scalingFactor` (scale 2, HALF_EVEN), where the
 * segment median is the median monthly quantity of all clients of the peer segment over the last 12 full
 * months, and `scalingFactor` defaults to parameter `peer.scaling_default` (1.0).
 *
 * No specification exists yet (backlog item `peer_benchmark_simulation`); the behaviour below is the
 * minimum the UI needs and is expected to change.
 *
 * @docs peer_benchmark_simulation
 */
object PeerBenchmark {

    data class PeerPoint(val period: YearMonth, val quantity: BigDecimal)

    /** Median of [values]; 0 for an empty list, mean of the two middle values for an even count. */
    fun median(values: List<BigDecimal>): BigDecimal {
        if (values.isEmpty()) return BigDecimal.ZERO
        val sorted = values.sorted()
        val mid = sorted.size / 2
        return if (sorted.size % 2 == 1) sorted[mid]
        else (sorted[mid - 1] + sorted[mid]).divide(bd(2), Rounding.RATIO_SCALE, Rounding.MODE)
    }

    /**
     * @param segmentQuantities per month, the monthly quantities of every client of the peer segment
     * @param scalingFactor multiplier applied to the segment median
     */
    fun simulate(segmentQuantities: Map<YearMonth, List<BigDecimal>>, scalingFactor: BigDecimal): List<PeerPoint> =
        segmentQuantities.entries
            .sortedBy { it.key }
            .map { (period, quantities) -> PeerPoint(period, (median(quantities) * scalingFactor).money()) }
}
