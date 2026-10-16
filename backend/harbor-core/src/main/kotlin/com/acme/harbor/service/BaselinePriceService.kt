package com.acme.harbor.service

import com.acme.harbor.client.rest.MarketDataClient
import com.acme.harbor.dao.repository.BaselinePriceRepository
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.dao.model.BaselinePrice
import com.acme.harbor.utils.MonthGrid
import com.acme.harbor.utils.Rounding
import com.acme.harbor.utils.toPeriodDate
import com.acme.harbor.utils.toYearMonth
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.Instant
import java.time.YearMonth

/**
 * Baseline price / transport price curve per product group, backed by `baseline_price`.
 * Months missing locally are fetched once from market-data. Also derives the price index used by the
 * projection: `priceIndex(m) = baseline(m) / baseline(first month of the horizon)` (scale 4).
 */
@Service
class BaselinePriceService(
    private val baselinePriceRepository: BaselinePriceRepository,
    private val marketData: MarketDataClient,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    data class Curve(val productGroup: ProductGroup, val asOf: Instant, val points: Map<YearMonth, Point>) {
        fun price(month: YearMonth): BigDecimal = points[month]?.price ?: BigDecimal.ZERO
        fun transportPrice(month: YearMonth): BigDecimal = points[month]?.transportPrice ?: BigDecimal.ZERO
        fun prices(grid: MonthGrid): List<BigDecimal> = grid.months.map { price(it) }
        fun transportPrices(grid: MonthGrid): List<BigDecimal> = grid.months.map { transportPrice(it) }

        /** Price relative to the first month of [grid]; 1.0000 when the first month has no price. */
        fun priceIndex(grid: MonthGrid): (YearMonth) -> BigDecimal {
            val base = price(grid.start)
            return { month -> if (base.signum() == 0) BigDecimal.ONE else price(month).divide(base, Rounding.RATIO_SCALE, Rounding.MODE) }
        }
    }

    data class Point(val price: BigDecimal, val transportPrice: BigDecimal)

    @Transactional
    fun curve(productGroup: ProductGroup, grid: MonthGrid): Curve {
        var rows = baselinePriceRepository.findAllByProductGroupAndPeriodBetweenOrderByPeriod(productGroup, grid.start.toPeriodDate(), grid.end.toPeriodDate())
        if (rows.map { it.period.toYearMonth() }.toSet() != grid.months.toSet()) {
            log.info("Baseline curve for {} incomplete locally, refreshing from market-data", productGroup)
            refresh(productGroup, grid.start, grid.end)
            rows = baselinePriceRepository.findAllByProductGroupAndPeriodBetweenOrderByPeriod(productGroup, grid.start.toPeriodDate(), grid.end.toPeriodDate())
        }
        return Curve(
            productGroup = productGroup,
            asOf = rows.maxOfOrNull { it.asOf } ?: Instant.EPOCH,
            points = rows.associate { it.period.toYearMonth() to Point(it.price, it.transportPrice) },
        )
    }

    /** Fetches both curves from market-data and upserts `baseline_price`. */
    @Transactional
    fun refresh(productGroup: ProductGroup, from: YearMonth, to: YearMonth): Int {
        val prices = marketData.prices(productGroup, from, to)
        val transport = marketData.transportPrices(productGroup)
        var count = 0
        prices.points.forEach { (month, price) ->
            val existing = baselinePriceRepository.findByProductGroupAndPeriod(productGroup, month.toPeriodDate())
            val transportPrice = transport.points[month] ?: existing?.transportPrice ?: BigDecimal.ZERO
            if (existing == null) {
                baselinePriceRepository.save(
                    BaselinePrice(
                        productGroup = productGroup,
                        corridor = productGroup.corridor,
                        period = month.toPeriodDate(),
                        price = price,
                        transportPrice = transportPrice,
                        asOf = prices.asOf,
                    ),
                )
            } else {
                existing.price = price
                existing.transportPrice = transportPrice
                existing.asOf = prices.asOf
            }
            count++
        }
        return count
    }
}
