package harbor.utils

import harbor.utils.StressTestCalculator.MonthInput
import harbor.enums.ClientRole
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import java.math.BigDecimal
import java.time.YearMonth

/** Worked examples of calculation `stress_test_monthly`. */
class StressTestCalculatorTest {

    private val m1 = YearMonth.of(2026, 1)
    private val m2 = YearMonth.of(2026, 2)

    private fun month(
        period: YearMonth,
        scenarioPrice: String,
        inbound: String = "100",
        outbound: String = "0",
    ) = MonthInput(
        period = period,
        dimensionValue = "Aldmoor",
        uncoveredInboundQty = bd(inbound),
        uncoveredOutboundQty = bd(outbound),
        totalQty = bd(150),
        baselinePrice = bd("10.00"),
        scenarioPrice = bd(scenarioPrice),
        baselineTransportPrice = bd("2.00"),
        scenarioTransportPrice = bd("2.50"),
    )

    @Test
    fun `importer - exposure, transport delta and cumulative over two months`() {
        val results = StressTestCalculator.run(ClientRole.IMPORTER, listOf(month(m1, "11.00"), month(m2, "12.00")))

        // month 1: exposure = 100 * (11 - 10) * +1 = 100.00; delta = 150 * (2.50 - 2.00) = 75.00
        assertEquals(bd("100.00"), results[0].exposure)
        assertEquals(bd("75.00"), results[0].transportCostDelta)
        assertEquals(bd("175.00"), results[0].cumulativeExposure)

        // month 2: exposure = 100 * (12 - 10) = 200.00; cumulative = 175 + 200 + 75 = 450.00
        assertEquals(bd("200.00"), results[1].exposure)
        assertEquals(bd("75.00"), results[1].transportCostDelta)
        assertEquals(bd("450.00"), results[1].cumulativeExposure)
    }

    @Test
    fun `exporter - same inputs give a negative exposure`() {
        val result = StressTestCalculator.run(ClientRole.EXPORTER, listOf(month(m1, "11.00"))).single()
        assertEquals(bd("-100.00"), result.exposure)
        assertEquals(bd("-25.00"), result.cumulativeExposure)
    }

    @Test
    fun `mixed - net direction quantity is used`() {
        // uncovered in 60 / out 40 -> net 20 -> exposure 20 * (11 - 10) = 20.00
        val result = StressTestCalculator.run(ClientRole.MIXED, listOf(month(m1, "11.00", inbound = "60", outbound = "40"))).single()
        assertEquals(bd("20.00"), result.exposure)
    }

    @Test
    fun `cumulative exposure runs per dimension value`() {
        val other = month(m1, "11.00").copy(dimensionValue = "Carrow", totalQty = BigDecimal.ZERO)
        val results = StressTestCalculator.run(ClientRole.IMPORTER, listOf(month(m1, "11.00"), other))
        assertEquals(bd("175.00"), results.first { it.dimensionValue == "Aldmoor" }.cumulativeExposure)
        assertEquals(bd("100.00"), results.first { it.dimensionValue == "Carrow" }.cumulativeExposure)
    }
}
