package com.bank.adv.hedges.calc

import java.math.BigDecimal
import java.time.YearMonth

/**
 * Monthly hedge cash-flow calculator.
 * @docs hedge_monthly_cashflow
 */
class HedgeCashflowCalculator(private val rates: RateProvider) {

    /**
     * Net monthly cash flow = notional * (fixedRate - floatingRate(month)) * dayCountFraction(month).
     * Positive = client receives.
     * @docs hedge_monthly_cashflow
     */
    fun monthlyCashflow(notional: BigDecimal, fixedRate: BigDecimal, month: YearMonth): BigDecimal {
        val floating = rates.floatingRate(month)
        return notional * (fixedRate - floating) * dayCountFraction(month)
    }

    /**
     * Stress test: re-prices every month under a shifted curve (parallel shift in bp).
     * @docs hedge_stress_test
     */
    fun stress(notional: BigDecimal, fixedRate: BigDecimal, months: List<YearMonth>, shiftBp: Int): List<BigDecimal> =
        months.map { monthlyCashflow(notional, fixedRate + BigDecimal(shiftBp).movePointLeft(4), it) }

    private fun dayCountFraction(month: YearMonth): BigDecimal =
        BigDecimal(month.lengthOfMonth()).divide(BigDecimal(360), 10, java.math.RoundingMode.HALF_EVEN)
}
