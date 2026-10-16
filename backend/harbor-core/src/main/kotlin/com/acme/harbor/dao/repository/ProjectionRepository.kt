package com.acme.harbor.dao.repository

import com.acme.harbor.dao.mapper.ProjectionRowMapper
import com.acme.harbor.enums.DimensionKind
import com.acme.harbor.model.ProjectionRow
import com.acme.harbor.utils.ProjectionAggregator.Line
import com.acme.harbor.utils.ProjectionAggregator.SummaryLine
import com.acme.harbor.utils.ProjectionAggregator.Tables
import com.acme.harbor.utils.toPeriodDate
import com.acme.harbor.utils.toYearMonth
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Repository
import org.springframework.transaction.annotation.Transactional
import java.sql.Date
import java.util.UUID

/**
 * Persists the four projection tables of a session (V5__projection.sql: `projection_by_subproduct`,
 * `projection_by_dimension`, `projection_by_direction`, `projection_summary`). The tables are a cache
 * of `ProjectionAggregator` output: every recompute replaces all rows of the session.
 * Plain JDBC batch inserts are used because the tables are write-once / read-many fact tables.
 */
@Repository
class ProjectionRepository(private val jdbc: JdbcTemplate) {

    @Transactional
    fun replace(sessionId: UUID, tables: Tables) {
        delete(sessionId)
        jdbc.batchUpdate(
            "insert into projection_by_subproduct (session_id, period, sub_product, quantity, value, landed_cost, cumulative_value) values (?,?,?,?,?,?,?)",
            tables.bySubProduct, BATCH_SIZE,
        ) { ps, l -> ps.setObject(1, sessionId); ps.setDate(2, Date.valueOf(l.period.toPeriodDate())); ps.setString(3, l.key); ps.setBigDecimal(4, l.quantity); ps.setBigDecimal(5, l.value); ps.setBigDecimal(6, l.landedCost); ps.setBigDecimal(7, l.cumulativeValue) }
        jdbc.batchUpdate(
            "insert into projection_by_dimension (session_id, period, dimension_kind, dimension_value, quantity, value, landed_cost, cumulative_value) values (?,?,?,?,?,?,?,?)",
            tables.byDimension, BATCH_SIZE,
        ) { ps, l -> ps.setObject(1, sessionId); ps.setDate(2, Date.valueOf(l.period.toPeriodDate())); ps.setString(3, tables.dimensionKind.name); ps.setString(4, l.key); ps.setBigDecimal(5, l.quantity); ps.setBigDecimal(6, l.value); ps.setBigDecimal(7, l.landedCost); ps.setBigDecimal(8, l.cumulativeValue) }
        jdbc.batchUpdate(
            "insert into projection_by_direction (session_id, period, direction, quantity, value, landed_cost, cumulative_value) values (?,?,?,?,?,?,?)",
            tables.byDirection, BATCH_SIZE,
        ) { ps, l -> ps.setObject(1, sessionId); ps.setDate(2, Date.valueOf(l.period.toPeriodDate())); ps.setString(3, l.key); ps.setBigDecimal(4, l.quantity); ps.setBigDecimal(5, l.value); ps.setBigDecimal(6, l.landedCost); ps.setBigDecimal(7, l.cumulativeValue) }
        jdbc.batchUpdate(
            "insert into projection_summary (session_id, period, total_quantity, total_value, total_landed_cost, cover_ratio, cumulative_value) values (?,?,?,?,?,?,?)",
            tables.summary, BATCH_SIZE,
        ) { ps, s -> ps.setObject(1, sessionId); ps.setDate(2, Date.valueOf(s.period.toPeriodDate())); ps.setBigDecimal(3, s.totalQuantity); ps.setBigDecimal(4, s.totalValue); ps.setBigDecimal(5, s.totalLandedCost); ps.setBigDecimal(6, s.coverRatio); ps.setBigDecimal(7, s.cumulativeValue) }
    }

    @Transactional
    fun delete(sessionId: UUID) {
        ProjectionRow.TABLES.forEach { jdbc.update("delete from $it where session_id = ?", sessionId) }
    }

    /** Stored tables of a session, or null when the projection has not been computed yet. */
    fun load(sessionId: UUID): Tables? {
        val summary = jdbc.query(
            "select period, total_quantity, total_value, total_landed_cost, cover_ratio, cumulative_value from projection_summary where session_id = ? order by period",
            { rs, _ -> SummaryLine(rs.getDate("period").toLocalDate().toYearMonth(), rs.getBigDecimal("total_quantity"), rs.getBigDecimal("total_value"), rs.getBigDecimal("total_landed_cost"), rs.getBigDecimal("cover_ratio"), rs.getBigDecimal("cumulative_value")) },
            sessionId,
        )
        if (summary.isEmpty()) return null
        val dimensionKind = jdbc.query("select distinct dimension_kind from projection_by_dimension where session_id = ?", { rs, _ -> DimensionKind.valueOf(rs.getString(1)) }, sessionId)
            .firstOrNull() ?: DimensionKind.CITY
        return Tables(
            dimensionKind = dimensionKind,
            bySubProduct = lines(ProjectionRow.BY_SUBPRODUCT, "select period, sub_product as k, quantity, value, landed_cost, cumulative_value from projection_by_subproduct where session_id = ? order by sub_product, period", sessionId),
            byDimension = lines(ProjectionRow.BY_DIMENSION, "select period, dimension_value as k, quantity, value, landed_cost, cumulative_value from projection_by_dimension where session_id = ? order by dimension_value, period", sessionId),
            byDirection = lines(ProjectionRow.BY_DIRECTION, "select period, direction as k, quantity, value, landed_cost, cumulative_value from projection_by_direction where session_id = ? order by direction, period", sessionId),
            summary = summary,
        )
    }

    fun exists(sessionId: UUID): Boolean =
        (jdbc.queryForObject("select count(*) from projection_summary where session_id = ?", Int::class.java, sessionId) ?: 0) > 0

    private fun lines(table: String, sql: String, sessionId: UUID): List<Line> =
        jdbc.query(sql, ProjectionRowMapper(table), sessionId).map { it.toLine() }

    private fun ProjectionRow.toLine() = Line(period, key, quantity, value, landedCost, cumulativeValue)

    companion object {
        private const val BATCH_SIZE = 500
    }
}
