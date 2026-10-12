package harbor.utils

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Worked examples of calculation `peer_benchmark_simulation` (executor of the concept):
 * segment median per month times the scaling factor, scale 2 HALF_EVEN.
 */
class PeerBenchmarkTest {

    private val jan = YearMonth.of(2026, 1)
    private val feb = YearMonth.of(2026, 2)

    @Test
    fun `median of an odd count is the middle value`() {
        assertEquals(bd("20"), PeerBenchmark.median(listOf(bd("30"), bd("10"), bd("20"))))
    }

    @Test
    fun `median of an even count is the mean of the two middle values at scale 4`() {
        assertEquals(bd("25.0000"), PeerBenchmark.median(listOf(bd("10"), bd("40"), bd("20"), bd("30"))))
    }

    @Test
    fun `median of no values is zero`() {
        assertEquals(BigDecimal.ZERO, PeerBenchmark.median(emptyList()))
    }

    @Test
    fun `peer quantity is the segment median times the scaling factor at scale 2 with months sorted`() {
        val points = PeerBenchmark.simulate(
            mapOf(
                feb to listOf(bd("10"), bd("40"), bd("20"), bd("30")),
                jan to listOf(bd("30"), bd("10"), bd("20")),
            ),
            bd("1.5"),
        )
        assertEquals(listOf(jan, feb), points.map { it.period })
        assertEquals(bd("30.00"), points[0].quantity) // median 20 * 1.5
        assertEquals(bd("37.50"), points[1].quantity) // median 25.0000 * 1.5
    }

    @Test
    fun `a month without peer data yields zero`() {
        val points = PeerBenchmark.simulate(mapOf(jan to emptyList()), bd("2"))
        assertEquals(bd("0.00"), points.single().quantity)
    }
}
