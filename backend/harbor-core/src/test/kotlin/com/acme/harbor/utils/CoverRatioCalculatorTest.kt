package com.acme.harbor.utils

import com.acme.harbor.utils.CoverRatioCalculator.PolicyTerms
import com.acme.harbor.utils.CoverRatioCalculator.ValueSlice
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import java.time.YearMonth

/** Worked examples of calculation `cover_ratio`. */
class CoverRatioCalculatorTest {

    private val month = YearMonth.of(2026, 3)
    private val policies = listOf(
        PolicyTerms(subProduct = "P1-STD", coveredShare = bd("0.6"), validFrom = YearMonth.of(2025, 1), validTo = null),
    )

    @Test
    fun `covered value and ratio of a month`() {
        // total 1000 = P1-STD 500 (policy share 0.6) + P1-PRM 500 (no policy)
        val slices = listOf(
            ValueSlice(month, "P1-STD", bd("500.00")),
            ValueSlice(month, "P1-PRM", bd("500.00")),
        )
        val result = CoverRatioCalculator.perMonth(slices, policies).single()
        assertEquals(bd("1000.00"), result.totalValue)
        assertEquals(bd("300.00"), result.coveredValue)
        assertEquals(bd("0.3000"), result.coverRatio)
    }

    @Test
    fun `ratio is zero when the total is zero`() {
        val slices = listOf(ValueSlice(month, "P1-STD", bd("0.00")))
        val result = CoverRatioCalculator.perMonth(slices, policies).single()
        assertEquals(bd("0.00"), result.coveredValue)
        assertEquals(bd("0.0000"), result.coverRatio)
    }

    @Test
    fun `policy outside its validity does not cover`() {
        val expired = listOf(PolicyTerms("P1-STD", bd("0.6"), YearMonth.of(2025, 1), YearMonth.of(2025, 12)))
        val slices = listOf(ValueSlice(month, "P1-STD", bd("500.00")))
        assertEquals(bd("0.0000"), CoverRatioCalculator.perMonth(slices, expired).single().coverRatio)
    }

    @Test
    fun `per sub-product series`() {
        val slices = listOf(
            ValueSlice(month, "P1-STD", bd("500.00")),
            ValueSlice(month, "P1-PRM", bd("500.00")),
        )
        val series = CoverRatioCalculator.perMonthAndSubProduct(slices, policies)
        assertEquals(bd("0.0000"), series.first { it.subProduct == "P1-PRM" }.coverRatio)
        assertEquals(bd("0.6000"), series.first { it.subProduct == "P1-STD" }.coverRatio)
    }
}
