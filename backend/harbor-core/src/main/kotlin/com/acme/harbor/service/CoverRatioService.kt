package com.acme.harbor.service

import com.acme.harbor.context.SessionScope
import com.acme.harbor.dao.repository.CoverPolicyRepository
import com.acme.harbor.dao.repository.MovementMonthlyRepository
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.utils.CoverRatioCalculator
import com.acme.harbor.utils.MonthGrid
import com.acme.harbor.utils.ProjectionAggregator.Tables
import com.acme.harbor.utils.Rounding
import com.acme.harbor.utils.sumMoney
import com.acme.harbor.utils.toPeriodDate
import com.acme.harbor.utils.toYearMonth
import org.springframework.stereotype.Service
import java.math.BigDecimal
import java.time.Clock
import java.time.LocalDate
import java.time.YearMonth
import java.util.UUID

/**
 * Applies calculation `cover_ratio` ([CoverRatioCalculator]) with the client's `cover_policy` rows:
 * - on the projection tables of a session (value by sub-product and month -> chart series and summary column),
 * - on the actual value of the last 12 full months (`movement_monthly`) for the client overview indicator.
 */
@Service
class CoverRatioService(
    private val policyRepository: CoverPolicyRepository,
    private val monthlyRepository: MovementMonthlyRepository,
    private val clock: Clock,
) {

    /** Cover of one projection: per month total, per month and sub-product, and the uncovered value. */
    data class CoverView(
        val perMonth: List<CoverRatioCalculator.CoverMonth>,
        val perSubProduct: List<CoverRatioCalculator.CoverMonth>,
    ) {
        val ratioByPeriod: Map<YearMonth, BigDecimal> get() = perMonth.associate { it.period to it.coverRatio }
        val uncoveredValue: BigDecimal get() = perMonth.map { it.totalValue - it.coveredValue }.sumMoney()
    }

    fun policies(clientId: UUID, productGroup: ProductGroup): List<CoverRatioCalculator.PolicyTerms> =
        policyRepository.findAllByClientIdAndProductGroup(clientId, productGroup).map { it.toTerms() }

    /** Cover ratio of the session projection [tables], optionally restricted to [subProducts] and a period range. */
    fun cover(
        scope: SessionScope,
        tables: Tables,
        subProducts: Collection<String>? = null,
        from: YearMonth? = null,
        to: YearMonth? = null,
    ): CoverView {
        val policies = policies(scope.clientId, scope.productGroup)
        val slices = tables.bySubProduct
            .filter { subProducts == null || it.key in subProducts }
            .filter { (from == null || !it.period.isBefore(from)) && (to == null || !it.period.isAfter(to)) }
            .map { CoverRatioCalculator.ValueSlice(it.period, it.key, it.value) }
        return CoverView(
            perMonth = CoverRatioCalculator.perMonth(slices, policies),
            perSubProduct = CoverRatioCalculator.perMonthAndSubProduct(slices, policies),
        )
    }

    /** Cover ratio of the actual value of the last 12 full months (client overview indicator). */
    fun lastTwelveMonthsRatio(clientId: UUID, productGroup: ProductGroup): BigDecimal {
        val months = MonthGrid.lastFullMonths(LocalDate.now(clock))
        val slices = monthlyRepository.findAllByClientIdAndProductGroupAndPeriodBetween(
            clientId, productGroup, months.first().toPeriodDate(), months.last().toPeriodDate(),
        ).map { CoverRatioCalculator.ValueSlice(it.period.toYearMonth(), it.subProduct, it.value) }
        val perMonth = CoverRatioCalculator.perMonth(slices, policies(clientId, productGroup))
        val total = perMonth.fold(BigDecimal.ZERO) { acc, m -> acc + m.totalValue }
        val covered = perMonth.fold(BigDecimal.ZERO) { acc, m -> acc + m.coveredValue }
        return Rounding.divideAsRatio(covered, total)
    }
}
