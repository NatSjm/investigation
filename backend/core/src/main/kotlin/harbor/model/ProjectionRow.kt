package harbor.model

import java.math.BigDecimal
import java.time.YearMonth

/**
 * One stored line of the projection tables of a session (V5__projection.sql), as read by `ProjectionDao`
 * before it is turned back into `ProjectionAggregator.Line`. [key] is the sub-product, dimension value or
 * direction, depending on the table.
 */
data class ProjectionRow(
    val table: String,
    val period: YearMonth,
    val key: String,
    val quantity: BigDecimal,
    val value: BigDecimal,
    val landedCost: BigDecimal,
    val cumulativeValue: BigDecimal,
) {
    companion object {
        const val BY_SUBPRODUCT = "projection_by_subproduct"
        const val BY_DIMENSION = "projection_by_dimension"
        const val BY_DIRECTION = "projection_by_direction"
        const val SUMMARY = "projection_summary"

        val TABLES: List<String> = listOf(BY_SUBPRODUCT, BY_DIMENSION, BY_DIRECTION, SUMMARY)
    }
}
