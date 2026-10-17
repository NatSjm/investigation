package com.acme.harbor.utils

import java.time.LocalDate
import java.time.YearMonth

/**
 * The planning horizon of a session as an ordered list of calendar months.
 *
 * A grid starts at [start] (the first month of the projection, normally the month after the last full
 * actual month) and spans [horizonMonths] months (12..60, parameter `projection.horizon_months_default`).
 * Scenario shocks refer to months by their 1-based index in this grid (`fromMonth`).
 */
class MonthGrid(val start: YearMonth, val horizonMonths: Int) : Iterable<YearMonth> {

    init {
        require(horizonMonths in MIN_HORIZON..MAX_HORIZON) {
            "horizonMonths must be between $MIN_HORIZON and $MAX_HORIZON, was $horizonMonths"
        }
    }

    val months: List<YearMonth> = (0 until horizonMonths).map { start.plusMonths(it.toLong()) }

    val end: YearMonth get() = months.last()

    /** 1-based index of [month] in the grid, or null when the month lies outside the horizon. */
    fun indexOf(month: YearMonth): Int? = months.indexOf(month).takeIf { it >= 0 }?.plus(1)

    fun contains(month: YearMonth): Boolean = month in months

    override fun iterator(): Iterator<YearMonth> = months.iterator()

    companion object {
        const val MIN_HORIZON = 12
        const val MAX_HORIZON = 60
        const val LOOKBACK_MONTHS = 12

        /** Grid starting with the month following [today]'s month. */
        fun startingAfter(today: LocalDate, horizonMonths: Int): MonthGrid =
            MonthGrid(YearMonth.from(today).plusMonths(1), horizonMonths)

        /** The last 12 full months before [today]'s month (used by the role classification). */
        fun lastFullMonths(today: LocalDate, count: Int = LOOKBACK_MONTHS): List<YearMonth> {
            val lastFull = YearMonth.from(today).minusMonths(1)
            return (count - 1 downTo 0).map { lastFull.minusMonths(it.toLong()) }
        }

        fun parse(period: String): YearMonth = YearMonth.parse(period)
    }
}

