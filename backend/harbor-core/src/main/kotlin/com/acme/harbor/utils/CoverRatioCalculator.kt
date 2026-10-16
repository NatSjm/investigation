package com.acme.harbor.utils

import java.math.BigDecimal
import java.time.YearMonth

/**
 * Cover ratio per month: which share of the projected value is covered by the client's policies.
 *
 * Definition, per month `m`:
 * - `coveredValue(m) = sum over rows of (value * coveredShare of the matching policy valid in m)`
 * - `coverRatio(m) = coveredValue(m) / totalValue(m)`, `0.0000` when `totalValue(m) = 0`
 * - `coveredValue` is money (scale 2), `coverRatio` a ratio (scale 4), both `HALF_EVEN`
 *
 * A policy matches a row when its `subProduct` equals the row's sub-product (a policy without sub-product
 * matches every sub-product of the product group) and `validFrom <= m <= validTo` (open `validTo` = no end).
 * When several policies match, the one with the latest `validFrom` applies; shares are never added up.
 *
 * Worked example: month total 1000 = P1-STD 500 (policy share 0.6) + P1-PRM 500 (no policy)
 * -> coveredValue 300.00, ratio 0.3000 (see `CoverRatioCalculatorTest`).
 *
 * @docs cover_ratio
 */
object CoverRatioCalculator {

    const val ALL = "ALL"

    data class PolicyTerms(
        val subProduct: String?,
        val coveredShare: BigDecimal,
        val validFrom: YearMonth,
        val validTo: YearMonth?,
    ) {
        fun matches(subProduct: String, period: YearMonth): Boolean =
            (this.subProduct == null || this.subProduct == subProduct) &&
                !period.isBefore(validFrom) && (validTo == null || !period.isAfter(validTo))
    }

    /** Projected value of one sub-product in one month (one `bySubProduct` line of the projection). */
    data class ValueSlice(val period: YearMonth, val subProduct: String, val value: BigDecimal)

    data class CoverMonth(
        val period: YearMonth,
        /** Sub-product, or [ALL] for the month total. */
        val subProduct: String,
        val totalValue: BigDecimal,
        val coveredValue: BigDecimal,
        val coverRatio: BigDecimal,
    )

    fun coveredShare(subProduct: String, period: YearMonth, policies: List<PolicyTerms>): BigDecimal =
        policies.filter { it.matches(subProduct, period) }
            .maxByOrNull { it.validFrom }
            ?.coveredShare
            ?: BigDecimal.ZERO

    fun coveredValue(slice: ValueSlice, policies: List<PolicyTerms>): BigDecimal =
        (slice.value * coveredShare(slice.subProduct, slice.period, policies)).money()

    /** Month totals over all sub-products (`subProduct = ALL`), ordered by period. */
    fun perMonth(slices: List<ValueSlice>, policies: List<PolicyTerms>): List<CoverMonth> =
        slices.groupBy { it.period }.entries.sortedBy { it.key }.map { (period, monthSlices) ->
            build(period, ALL, monthSlices, policies)
        }

    /** One entry per month and sub-product (the cover chart series of the product pages). */
    fun perMonthAndSubProduct(slices: List<ValueSlice>, policies: List<PolicyTerms>): List<CoverMonth> =
        slices.groupBy { it.period to it.subProduct }.entries
            .sortedWith(compareBy({ it.key.first }, { it.key.second }))
            .map { (key, group) -> build(key.first, key.second, group, policies) }

    /** Convenience for `projection_summary.cover_ratio`. */
    fun ratioByPeriod(slices: List<ValueSlice>, policies: List<PolicyTerms>): Map<YearMonth, BigDecimal> =
        perMonth(slices, policies).associate { it.period to it.coverRatio }

    private fun build(period: YearMonth, key: String, group: List<ValueSlice>, policies: List<PolicyTerms>): CoverMonth {
        val total = group.map { it.value }.sumMoney()
        val covered = group.map { coveredValue(it, policies) }.sumMoney()
        return CoverMonth(period, key, total, covered, Rounding.divideAsRatio(covered, total))
    }
}
