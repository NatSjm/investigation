package com.acme.harbor.utils

import java.math.BigDecimal
import java.time.LocalDate
import java.time.YearMonth

/*
 * Top-level extension functions shared by the calculations. This file declares no class: the generated maps list it
 * under its file name (`Extensions`), and its functions are reusable sub-calculations of the rounding and month
 * conventions documented in [Rounding] and [MonthGrid].
 */

/** Money rounding (scale 2, half even), see [Rounding.money]. */
fun BigDecimal.money(): BigDecimal = Rounding.money(this)

/** Ratio rounding (scale 4, half even), see [Rounding.ratio]. */
fun BigDecimal.ratio(): BigDecimal = Rounding.ratio(this)

/** Sum of money amounts, rounded once at the end (never per element). */
fun Iterable<BigDecimal>.sumMoney(): BigDecimal = fold(BigDecimal.ZERO) { acc, v -> acc + v }.money()

fun bd(value: String): BigDecimal = BigDecimal(value)

fun bd(value: Int): BigDecimal = BigDecimal.valueOf(value.toLong())

/** First day of the month, the representation used in the `period date` columns. */
fun YearMonth.toPeriodDate(): LocalDate = atDay(1)

fun LocalDate.toYearMonth(): YearMonth = YearMonth.from(this)
