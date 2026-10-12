package harbor.utils

import harbor.enums.DimensionKind
import harbor.enums.Direction
import harbor.enums.PriceBasis
import harbor.enums.TransportMode
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Monthly projection: values every movement row of a session over the planning horizon and groups the
 * result into the four cumulative tables (by sub-product, by dimension, by direction, summary).
 *
 * Definition, per month `m` of the horizon and per row:
 * - `value = quantity * unitPrice * priceIndex(m)`
 * - `landedCost = value * (1 + tariffRate(productGroup, country)) + quantity * handlingCost(city) + quantity * transportCost(mode)`
 * - rows are grouped into the four tables by summing `quantity`, `value`, `landedCost`
 * - `cumulativeValue` = running sum of `value` over the months of the horizon, per table key
 * - money is rounded `HALF_EVEN` to scale 2 at row level (`value`, `landedCost`); sums are not rounded again
 *
 * The country of the tariff rate is the price basis of the row (VLD/NRL for Product 1, CST/MRD for Product 2).
 *
 * Grouping is done here in Kotlin from a flat list of rows and not in SQL because the very same aggregation
 * is reused by the cover ratio (value per sub-product and month), the stress test (quantity per dimension
 * value and month) and the report payload; one implementation keeps the four tables and these consumers
 * consistent.
 *
 * The horizon totals ([totals], calculation `horizon_totals`) are derived from the four tables: every table is summed over
 * the whole horizon per key and an overall line is added, so the overview can show the breakdown without months.
 *
 * Worked examples: see `ProjectionAggregatorTest`.
 *
 * @docs monthly_projection
 * @docs horizon_totals
 */
object ProjectionAggregator {

    /** One movement in one month: an actual monthly rollup, a modelled input or a peer simulation point. */
    data class Row(
        val period: YearMonth,
        val subProduct: String,
        val city: String?,
        val transportMode: TransportMode?,
        val direction: Direction,
        val quantity: BigDecimal,
        val unitPrice: BigDecimal,
        val priceBasis: PriceBasis,
    )

    /** Parameter lookups needed by the formulas; resolved by the calling service from `parameter_set` and `baseline_price`. */
    class Context(
        val priceIndex: (YearMonth) -> BigDecimal,
        val tariffRate: (PriceBasis) -> BigDecimal,
        val handlingCost: (String?) -> BigDecimal,
        val transportCost: (TransportMode?) -> BigDecimal,
    )

    data class ValuedRow(val row: Row, val value: BigDecimal, val landedCost: BigDecimal)

    data class Line(
        val period: YearMonth,
        val key: String,
        val quantity: BigDecimal,
        val value: BigDecimal,
        val landedCost: BigDecimal,
        val cumulativeValue: BigDecimal,
    )

    data class SummaryLine(
        val period: YearMonth,
        val totalQuantity: BigDecimal,
        val totalValue: BigDecimal,
        val totalLandedCost: BigDecimal,
        /** Filled in by ProjectionService through [withCoverRatio] (calculation `cover_ratio`); 0.0000 until then. */
        val coverRatio: BigDecimal,
        val cumulativeValue: BigDecimal,
    )

    /** One key of a monthly table summed over the whole horizon; `shareOfValue` = key value / overall value (scale 4). */
    data class Total(
        val key: String,
        val quantity: BigDecimal,
        val value: BigDecimal,
        val landedCost: BigDecimal,
        val shareOfValue: BigDecimal,
    )

    /** Horizon totals of the three breakdown tables plus the overall line (key [ALL]); calculation `horizon_totals`. */
    data class Totals(
        val bySubProduct: List<Total>,
        val byDimension: List<Total>,
        val byDirection: List<Total>,
        val overall: Total,
    )

    data class Tables(
        val dimensionKind: DimensionKind,
        val bySubProduct: List<Line>,
        val byDimension: List<Line>,
        val byDirection: List<Line>,
        val summary: List<SummaryLine>,
    ) {
        /** Derived, never persisted: the totals are recomputed from the monthly lines wherever the tables are loaded. */
        val totals: Totals get() = totals(this)

        fun withCoverRatio(ratioByPeriod: Map<YearMonth, BigDecimal>): Tables =
            copy(summary = summary.map { it.copy(coverRatio = ratioByPeriod[it.period] ?: Rounding.ZERO_RATIO) })
    }

    fun valueRow(row: Row, context: Context): ValuedRow {
        val value = (row.quantity * row.unitPrice * context.priceIndex(row.period)).money()
        val landedCost = (
            value * (BigDecimal.ONE + context.tariffRate(row.priceBasis)) +
                row.quantity * context.handlingCost(row.city) +
                row.quantity * context.transportCost(row.transportMode)
            ).money()
        return ValuedRow(row, value, landedCost)
    }

    fun aggregate(rows: List<Row>, grid: MonthGrid, dimensionKind: DimensionKind, context: Context): Tables {
        val valued = rows.filter { grid.contains(it.period) }.map { valueRow(it, context) }
        return Tables(
            dimensionKind = dimensionKind,
            bySubProduct = group(valued, grid) { it.row.subProduct },
            byDimension = group(valued, grid) { dimensionValue(it.row, dimensionKind) },
            byDirection = group(valued, grid) { it.row.direction.name },
            summary = summarize(valued, grid),
        )
    }

    fun dimensionValue(row: Row, kind: DimensionKind): String = when (kind) {
        DimensionKind.CITY -> row.city ?: UNKNOWN
        DimensionKind.TRANSPORT_MODE -> row.transportMode?.name ?: UNKNOWN
    }

    /** One line per key and month of the grid (zero lines included), cumulative value running per key. */
    fun group(valued: List<ValuedRow>, grid: MonthGrid, key: (ValuedRow) -> String): List<Line> {
        val keys = valued.map(key).distinct().sorted()
        val byKeyAndPeriod = valued.groupBy { key(it) to it.row.period }
        return keys.flatMap { k ->
            var cumulative = BigDecimal.ZERO
            grid.months.map { period ->
                val bucket = byKeyAndPeriod[k to period].orEmpty()
                val value = bucket.map { it.value }.sumMoney()
                cumulative += value
                Line(
                    period = period,
                    key = k,
                    quantity = bucket.map { it.row.quantity }.sumMoney(),
                    value = value,
                    landedCost = bucket.map { it.landedCost }.sumMoney(),
                    cumulativeValue = cumulative.money(),
                )
            }
        }
    }

    /**
     * Horizon totals: each monthly table summed over the whole horizon per key, plus the overall line from the summary
     * table. The sums add the already rounded monthly figures (no second rounding, no drift); `shareOfValue` is the
     * key's value divided by the overall value, scale 4 HALF_EVEN, `0.0000` when the overall value is zero. The keys
     * of each breakdown add up to the overall line by construction.
     *
     * @docs horizon_totals
     */
    fun totals(tables: Tables): Totals {
        val overallValue = tables.summary.map { it.totalValue }.sumMoney()
        val overall = Total(
            key = ALL,
            quantity = tables.summary.map { it.totalQuantity }.sumMoney(),
            value = overallValue,
            landedCost = tables.summary.map { it.totalLandedCost }.sumMoney(),
            shareOfValue = if (overallValue.signum() == 0) Rounding.ZERO_RATIO else BigDecimal.ONE.ratio(),
        )
        return Totals(
            bySubProduct = totalsOf(tables.bySubProduct, overallValue),
            byDimension = totalsOf(tables.byDimension, overallValue),
            byDirection = totalsOf(tables.byDirection, overallValue),
            overall = overall,
        )
    }

    /** One total per key, keys sorted as in the monthly tables. */
    fun totalsOf(lines: List<Line>, overallValue: BigDecimal): List<Total> =
        lines.groupBy { it.key }.toSortedMap().map { (key, perMonth) ->
            val value = perMonth.map { it.value }.sumMoney()
            Total(
                key = key,
                quantity = perMonth.map { it.quantity }.sumMoney(),
                value = value,
                landedCost = perMonth.map { it.landedCost }.sumMoney(),
                shareOfValue = Rounding.divideAsRatio(value, overallValue),
            )
        }

    private fun summarize(valued: List<ValuedRow>, grid: MonthGrid): List<SummaryLine> {
        val byPeriod = valued.groupBy { it.row.period }
        var cumulative = BigDecimal.ZERO
        return grid.months.map { period ->
            val bucket = byPeriod[period].orEmpty()
            val value = bucket.map { it.value }.sumMoney()
            cumulative += value
            SummaryLine(
                period = period,
                totalQuantity = bucket.map { it.row.quantity }.sumMoney(),
                totalValue = value,
                totalLandedCost = bucket.map { it.landedCost }.sumMoney(),
                coverRatio = Rounding.ZERO_RATIO,
                cumulativeValue = cumulative.money(),
            )
        }
    }

    const val UNKNOWN = "UNKNOWN"
    const val ALL = "ALL"
}
