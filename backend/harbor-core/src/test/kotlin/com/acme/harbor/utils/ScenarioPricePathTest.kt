package com.acme.harbor.utils

import com.acme.harbor.utils.ScenarioPricePath.Shock
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/** Worked examples of calculation `scenario_price_path`. */
class ScenarioPricePathTest {

    private val baseline = listOf(bd(10), bd(10), bd(10), bd(10))

    @Test
    fun `shocks are cumulative from their month onwards`() {
        val shocks = listOf(
            Shock(fromMonth = 2, priceChangePct = bd("0.10")),
            Shock(fromMonth = 3, priceChangePct = bd("0.05")),
        )
        val path = ScenarioPricePath.pricePath(baseline, shocks)
        assertEquals(listOf(bd("10.00"), bd("11.00"), bd("11.55"), bd("11.55")), path)
    }

    @Test
    fun `no shocks returns the baseline at money scale`() {
        assertEquals(listOf(bd("10.00"), bd("10.00"), bd("10.00"), bd("10.00")), ScenarioPricePath.pricePath(baseline, emptyList()))
    }

    @Test
    fun `transport path uses transportChangePct only`() {
        val shocks = listOf(Shock(fromMonth = 1, priceChangePct = bd("0.10"), transportChangePct = bd("0.25")))
        val transport = ScenarioPricePath.transportPath(listOf(bd(2), bd(2)), shocks)
        assertEquals(listOf(bd("2.50"), bd("2.50")), transport)
    }
}
