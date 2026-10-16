package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.CoverSeriesPoint
import com.acme.harbor.api.generated.model.MovementInputList
import com.acme.harbor.api.generated.model.PeerSimulationResult
import com.acme.harbor.api.generated.model.ProductOverview
import com.acme.harbor.api.generated.model.Projection
import com.acme.harbor.api.generated.model.ProjectionLine
import com.acme.harbor.api.generated.model.ProjectionTables
import com.acme.harbor.api.generated.model.ProjectionTotal
import com.acme.harbor.api.generated.model.ProjectionTotals
import com.acme.harbor.api.generated.model.SparklinePoint
import com.acme.harbor.api.generated.model.SummaryLine
import com.acme.harbor.context.SessionScope
import com.acme.harbor.enums.Direction
import com.acme.harbor.enums.TransportMode
import com.acme.harbor.service.PeerSimulationService
import com.acme.harbor.service.ProjectionService
import com.acme.harbor.service.ProjectionService.MovementInputCommand
import com.acme.harbor.utils.CoverRatioCalculator
import com.acme.harbor.utils.ProjectionAggregator
import com.acme.harbor.utils.ProjectionAggregator.Tables
import java.time.OffsetDateTime
import java.time.YearMonth
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.ClientRole as ApiClientRole
import com.acme.harbor.api.generated.model.DimensionKind as ApiDimensionKind
import com.acme.harbor.api.generated.model.ProductGroup as ApiProductGroup

/** Maps projection tables, overview and modal payloads to the generated API models (shared by Product 1 and Product 2). */
object ProjectionMapper {

    fun line(l: ProjectionAggregator.Line) = ProjectionLine(
        period = l.period.toString(), key = l.key, quantity = l.quantity, value = l.value,
        landedCost = l.landedCost, cumulativeValue = l.cumulativeValue,
    )

    fun summary(s: ProjectionAggregator.SummaryLine) = SummaryLine(
        period = s.period.toString(), totalQuantity = s.totalQuantity, totalValue = s.totalValue,
        totalLandedCost = s.totalLandedCost, coverRatio = s.coverRatio, cumulativeValue = s.cumulativeValue,
    )

    fun total(t: ProjectionAggregator.Total) = ProjectionTotal(
        key = t.key, quantity = t.quantity, value = t.value, landedCost = t.landedCost, shareOfValue = t.shareOfValue,
    )

    fun totals(t: ProjectionAggregator.Totals) = ProjectionTotals(
        bySubProduct = t.bySubProduct.map(::total),
        byDimension = t.byDimension.map(::total),
        byDirection = t.byDirection.map(::total),
        overall = total(t.overall),
    )

    fun tables(t: Tables) = ProjectionTables(
        dimensionKind = ApiDimensionKind.valueOf(t.dimensionKind.name),
        bySubProduct = t.bySubProduct.map(::line),
        byDimension = t.byDimension.map(::line),
        byDirection = t.byDirection.map(::line),
        summary = t.summary.map(::summary),
        totals = totals(t.totals),
    )

    fun projection(scope: SessionScope, t: Tables) = Projection(
        sessionId = scope.sessionId,
        horizonMonths = scope.horizonMonths,
        computedAt = OffsetDateTime.now(ZoneOffset.UTC),
        tables = tables(t),
    )

    fun coverPoint(c: CoverRatioCalculator.CoverMonth) =
        CoverSeriesPoint(period = c.period.toString(), subProduct = c.subProduct, coverRatio = c.coverRatio)

    fun overview(scope: SessionScope, o: ProjectionService.Overview) = ProductOverview(
        sessionId = scope.sessionId,
        productGroup = ApiProductGroup.valueOf(scope.productGroup.wireValue),
        dimensionFilter = o.dimensionFilter,
        role = ApiClientRole.valueOf(o.role.name),
        tables = tables(o.tables),
        coverSeries = o.coverSeries.map(::coverPoint),
    )

    fun movementInputs(list: MovementInputList): List<MovementInputCommand> = list.movements.map {
        MovementInputCommand(
            period = YearMonth.parse(it.period),
            subProduct = it.subProduct,
            city = it.city,
            transportMode = it.transportMode?.let { mode -> TransportMode.valueOf(mode.name) },
            direction = Direction.valueOf(it.direction.name),
            quantity = it.quantity,
            unitPrice = it.unitPrice,
        )
    }

    fun peerResult(r: PeerSimulationService.Result) = PeerSimulationResult(
        simulationId = r.simulation.id,
        peerSegment = r.simulation.peerSegment,
        scalingFactor = r.simulation.scalingFactor,
        generatedAt = r.simulation.generatedAt.atOffset(ZoneOffset.UTC),
        series = r.series.map { SparklinePoint(period = it.period.toString(), value = it.quantity) },
    )
}
