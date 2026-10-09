package harbor.utils

import java.math.BigDecimal
import java.math.RoundingMode

/**
 * Rounding conventions shared by all calculations.
 *
 * - Money amounts (value, landed cost, exposure, premium): scale 2.
 * - Ratios and shares (cover ratio, role share, scaling factors): scale 4.
 * - Rounding mode is always `HALF_EVEN` (round half to even) so that repeated aggregation does not drift.
 *
 * Every calculation rounds at the point where a figure becomes an output (per row / per month) and
 * never rounds intermediate products.
 */
object Rounding {
    const val MONEY_SCALE: Int = 2
    const val RATIO_SCALE: Int = 4
    val MODE: RoundingMode = RoundingMode.HALF_EVEN

    fun money(value: BigDecimal): BigDecimal = value.setScale(MONEY_SCALE, MODE)

    fun ratio(value: BigDecimal): BigDecimal = value.setScale(RATIO_SCALE, MODE)

    /** Division that yields a ratio (scale 4); returns 0.0000 when the divisor is zero. */
    fun divideAsRatio(numerator: BigDecimal, denominator: BigDecimal): BigDecimal =
        if (denominator.signum() == 0) ZERO_RATIO
        else numerator.divide(denominator, RATIO_SCALE, MODE)

    val ZERO_MONEY: BigDecimal = BigDecimal.ZERO.setScale(MONEY_SCALE)
    val ZERO_RATIO: BigDecimal = BigDecimal.ZERO.setScale(RATIO_SCALE)
}

/** Extension shortcuts used throughout the calculations in `harbor.utils`. */
fun BigDecimal.money(): BigDecimal = Rounding.money(this)

fun BigDecimal.ratio(): BigDecimal = Rounding.ratio(this)

fun Iterable<BigDecimal>.sumMoney(): BigDecimal = fold(BigDecimal.ZERO) { acc, v -> acc + v }.money()

fun bd(value: String): BigDecimal = BigDecimal(value)

fun bd(value: Int): BigDecimal = BigDecimal.valueOf(value.toLong())
