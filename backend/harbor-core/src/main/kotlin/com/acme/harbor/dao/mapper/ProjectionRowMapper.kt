package com.acme.harbor.dao.mapper

import com.acme.harbor.model.ProjectionRow
import com.acme.harbor.utils.toYearMonth
import org.springframework.jdbc.core.RowMapper
import java.sql.ResultSet

/** Maps one row of a projection table (`period, k, quantity, value, landed_cost, cumulative_value`) to a [ProjectionRow]. */
class ProjectionRowMapper(private val table: String) : RowMapper<ProjectionRow> {

    override fun mapRow(rs: ResultSet, rowNum: Int): ProjectionRow = ProjectionRow(
        table = table,
        period = rs.getDate("period").toLocalDate().toYearMonth(),
        key = rs.getString("k"),
        quantity = rs.getBigDecimal("quantity"),
        value = rs.getBigDecimal("value"),
        landedCost = rs.getBigDecimal("landed_cost"),
        cumulativeValue = rs.getBigDecimal("cumulative_value"),
    )
}
