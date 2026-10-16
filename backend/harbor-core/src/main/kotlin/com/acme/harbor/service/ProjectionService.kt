package com.acme.harbor.service

import com.acme.harbor.context.SessionScope
import com.acme.harbor.dao.repository.ProjectionRepository
import com.acme.harbor.dao.repository.SessionMovementInputRepository
import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.Direction
import com.acme.harbor.enums.TransportMode
import com.acme.harbor.dao.model.SessionMovementInput
import com.acme.harbor.utils.CoverRatioCalculator
import com.acme.harbor.utils.ProjectionAggregator
import com.acme.harbor.utils.ProjectionAggregator.Row
import com.acme.harbor.utils.ProjectionAggregator.Tables
import com.acme.harbor.utils.toPeriodDate
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Product-agnostic projection pipeline of a session (calculation `monthly_projection`):
 * assemble rows ([ProjectionInputAssembler]) -> `ProjectionAggregator` -> cover ratio ([CoverRatioService])
 * -> store in the four projection tables ([ProjectionRepository]). `Product1Manager` / `Product2Manager` add the
 * product specific overview filter (city hub / transport mode) on top.
 */
@Service
class ProjectionService(
    private val assembler: ProjectionInputAssembler,
    private val projectionRepository: ProjectionRepository,
    private val inputRepository: SessionMovementInputRepository,
    private val coverRatioService: CoverRatioService,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    /** One modelled movement of the movement modal (modal 1). */
    data class MovementInputCommand(
        val period: YearMonth,
        val subProduct: String,
        val city: String?,
        val transportMode: TransportMode?,
        val direction: Direction,
        val quantity: BigDecimal,
        val unitPrice: BigDecimal,
    )

    /** Content of a product overview page (shared by Product 1 and Product 2). */
    data class Overview(
        val tables: Tables,
        val coverSeries: List<CoverRatioCalculator.CoverMonth>,
        val role: ClientRole,
        val dimensionFilter: String?,
    )

    /** Aggregates the (optionally filtered) rows without storing anything; used by the overview filters. */
    fun compute(scope: SessionScope, rowFilter: (Row) -> Boolean = { true }): Tables {
        val grid = assembler.grid(scope)
        val rows = assembler.rows(scope, grid).filter(rowFilter)
        val tables = ProjectionAggregator.aggregate(rows, grid, scope.productGroup.dimensionKind, assembler.context(scope, grid))
        return tables.withCoverRatio(coverRatioService.cover(scope, tables).ratioByPeriod)
    }

    /** Recomputes and replaces the stored tables of the session. */
    @Transactional
    fun recompute(scope: SessionScope): Tables {
        val tables = compute(scope)
        projectionRepository.replace(scope.sessionId, tables)
        log.debug("Projection of session {} stored ({} months)", scope.sessionId, tables.summary.size)
        return tables
    }

    /** Stored tables, computed on first access. */
    @Transactional
    fun loadOrCompute(scope: SessionScope): Tables = projectionRepository.load(scope.sessionId) ?: recompute(scope)

    /** Replaces the modelled movements of the session (movement modal) and recomputes; inputs are validated by the caller. */
    @Transactional
    fun replaceMovements(scope: SessionScope, inputs: List<MovementInputCommand>): Tables {
        inputRepository.deleteAllBySessionId(scope.sessionId)
        inputRepository.saveAll(
            inputs.map {
                SessionMovementInput(
                    sessionId = scope.sessionId,
                    period = it.period.toPeriodDate(),
                    subProduct = it.subProduct,
                    city = it.city,
                    transportMode = it.transportMode,
                    direction = it.direction,
                    quantity = it.quantity,
                    unitPrice = it.unitPrice,
                )
            },
        )
        return recompute(scope)
    }

    /** Overview content for [tables]: cover series per sub-product plus the role shown in the page header. */
    fun overview(scope: SessionScope, tables: Tables, role: ClientRole, dimensionFilter: String?): Overview =
        Overview(
            tables = tables,
            coverSeries = coverRatioService.cover(scope, tables).perSubProduct,
            role = role,
            dimensionFilter = dimensionFilter,
        )
}
