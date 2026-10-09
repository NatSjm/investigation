package harbor.mapper

import harbor.api.generated.model.CoverSeriesPoint
import harbor.api.generated.model.MovementInputList
import harbor.api.generated.model.PeerSimulationResult
import harbor.api.generated.model.ProductOverview
import harbor.api.generated.model.Projection
import harbor.api.generated.model.ProjectionLine
import harbor.api.generated.model.ProjectionTables
import harbor.api.generated.model.SparklinePoint
import harbor.api.generated.model.SummaryLine
import harbor.context.SessionScope
import harbor.enums.Direction
import harbor.enums.TransportMode
import harbor.service.PeerSimulationService
import harbor.service.ProjectionService
import harbor.service.ProjectionService.MovementInputCommand
import harbor.utils.CoverRatioCalculator
import harbor.utils.ProjectionAggregator
import harbor.utils.ProjectionAggregator.Tables
import java.time.OffsetDateTime
import java.time.YearMonth
import java.time.ZoneOffset
import harbor.api.generated.model.ClientRole as ApiClientRole
import harbor.api.generated.model.DimensionKind as ApiDimensionKind
import harbor.api.generated.model.ProductGroup as ApiProductGroup

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

    fun tables(t: Tables) = ProjectionTables(
        dimensionKind = ApiDimensionKind.valueOf(t.dimensionKind.name),
        bySubProduct = t.bySubProduct.map(::line),
        byDimension = t.byDimension.map(::line),
        byDirection = t.byDirection.map(::line),
        summary = t.summary.map(::summary),
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
