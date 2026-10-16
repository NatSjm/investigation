package com.acme.harbor.utils

import com.acme.harbor.utils.ProjectionAggregator.Context
import com.acme.harbor.utils.ProjectionAggregator.Row
import com.acme.harbor.enums.DimensionKind
import com.acme.harbor.enums.Direction
import com.acme.harbor.enums.PriceBasis
import com.acme.harbor.enums.TransportMode
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Worked examples of calculation `monthly_projection`.
 * Parameters: tariff.rate(product1, VLD) = 0.05, handling.cost(Aldmoor) = 0.80, transport.cost(ROAD) = 1.20.
 */
class ProjectionAggregatorTest {

    private val m1 = YearMonth.of(2026, 1)
    private val m2 = YearMonth.of(2026, 2)
    private val grid = MonthGrid(m1, 12)

    private val context = Context(
        priceIndex = { month -> if (month == m2) bd("1.06") else bd("1.04") },
        tariffRate = { bd("0.05") },
        handlingCost = { city -> if (city == "Aldmoor") bd("0.80") else BigDecimal.ZERO },
        transportCost = { mode -> if (mode == TransportMode.ROAD) bd("1.20") else BigDecimal.ZERO },
    )

    private fun row(period: YearMonth, qty: String = "100", unitPrice: String = "12.50") = Row(
        period = period,
        subProduct = "P1-STD",
        city = "Aldmoor",
        transportMode = TransportMode.ROAD,
        direction = Direction.IN,
        quantity = bd(qty),
        unitPrice = bd(unitPrice),
        priceBasis = PriceBasis.VLD,
    )

    @Test
    fun `value and landed cost of one row`() {
        // value = 100 * 12.50 * 1.04 = 1300.00
        // landedCost = 1300.00 * 1.05 + 100 * 0.80 + 100 * 1.20 = 1565.00
        val valued = ProjectionAggregator.valueRow(row(m1), context)
        assertEquals(bd("1300.00"), valued.value)
        assertEquals(bd("1565.00"), valued.landedCost)
    }

    @Test
    fun `second month with price index 1_06 and cumulative value`() {
        val tables = ProjectionAggregator.aggregate(listOf(row(m1), row(m2)), grid, DimensionKind.CITY, context)
        val lines = tables.bySubProduct.filter { it.key == "P1-STD" }

        val first = lines.first { it.period == m1 }
        assertEquals(bd("1300.00"), first.value)
        assertEquals(bd("1565.00"), first.landedCost)
        assertEquals(bd("1300.00"), first.cumulativeValue)

        val second = lines.first { it.period == m2 }
        assertEquals(bd("1325.00"), second.value)
        assertEquals(bd("1591.25"), second.landedCost)
        assertEquals(bd("2625.00"), second.cumulativeValue)
    }

    @Test
    fun `four tables share the same totals per month`() {
        val tables = ProjectionAggregator.aggregate(listOf(row(m1), row(m2)), grid, DimensionKind.CITY, context)
        assertEquals(bd("1300.00"), tables.byDimension.first { it.key == "Aldmoor" && it.period == m1 }.value)
        assertEquals(bd("1300.00"), tables.byDirection.first { it.key == "IN" && it.period == m1 }.value)
        assertEquals(bd("1300.00"), tables.summary.first { it.period == m1 }.totalValue)
        assertEquals(bd("2625.00"), tables.summary.first { it.period == m2 }.cumulativeValue)
        assertEquals(12, tables.summary.size)
    }

    @Test
    fun `horizon totals sum the monthly tables per key and share the overall value`() {
        // calculation horizon_totals: P1-STD = 1300.00 + 1325.00 = 2625.00 (landed 1565.00 + 1591.25 = 3156.25);
        // P1-PRM out of Carrow in month 2: value 1325.00, landed 1325.00 * 1.05 + 100 * 1.20 = 1511.25; overall 3950.00
        val prm = row(m2).copy(subProduct = "P1-PRM", city = "Carrow", direction = Direction.OUT)
        val totals = ProjectionAggregator.aggregate(listOf(row(m1), row(m2), prm), grid, DimensionKind.CITY, context).totals

        val std = totals.bySubProduct.first { it.key == "P1-STD" }
        assertEquals(bd("200.00"), std.quantity)
        assertEquals(bd("2625.00"), std.value)
        assertEquals(bd("3156.25"), std.landedCost)
        assertEquals(bd("0.6646"), std.shareOfValue) // 2625.00 / 3950.00
        assertEquals(bd("1511.25"), totals.bySubProduct.first { it.key == "P1-PRM" }.landedCost)
        assertEquals(bd("1325.00"), totals.byDimension.first { it.key == "Carrow" }.value)
        assertEquals(bd("1325.00"), totals.byDirection.first { it.key == "OUT" }.value)
        assertEquals(bd("3950.00"), totals.overall.value)
        assertEquals(bd("1.0000"), totals.overall.shareOfValue)
        assertEquals(totals.overall.value, totals.bySubProduct.map { it.value }.sumMoney())
    }

    @Test
    fun `horizon totals of an empty projection are zero`() {
        val totals = ProjectionAggregator.aggregate(emptyList(), grid, DimensionKind.CITY, context).totals
        assertEquals(bd("0.00"), totals.overall.value)
        assertEquals(bd("0.0000"), totals.overall.shareOfValue)
        assertEquals(emptyList<ProjectionAggregator.Total>(), totals.bySubProduct)
    }

    @Test
    fun `rounding is HALF_EVEN at scale 2`() {
        val unit = Context({ BigDecimal.ONE }, { BigDecimal.ZERO }, { BigDecimal.ZERO }, { BigDecimal.ZERO })
        assertEquals(bd("1.00"), ProjectionAggregator.valueRow(row(m1, qty = "1", unitPrice = "1.005"), unit).value)
        assertEquals(bd("1.02"), ProjectionAggregator.valueRow(row(m1, qty = "1", unitPrice = "1.015"), unit).value)
    }
}
