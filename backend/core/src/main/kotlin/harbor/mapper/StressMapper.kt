package harbor.mapper

import harbor.api.generated.model.StressTestResult
import harbor.api.generated.model.StressTestRow
import harbor.api.generated.model.StressTestScenarioResult
import harbor.enums.StressDimension
import harbor.manager.StressManager
import harbor.utils.StressTestCalculator
import java.time.ZoneOffset
import harbor.api.generated.model.ClientRole as ApiClientRole
import harbor.api.generated.model.DimensionKind as ApiDimensionKind

/** Maps stress test results to the generated API models. */
object StressMapper {

    fun ApiDimensionKind.toDomain(): StressDimension = StressDimension.valueOf(name)

    fun row(r: StressTestCalculator.MonthResult) = StressTestRow(
        period = r.period.toString(),
        dimensionValue = r.dimensionValue,
        scenarioPrice = r.scenarioPrice,
        scenarioTransportPrice = r.scenarioTransportPrice,
        exposure = r.exposure,
        transportCostDelta = r.transportCostDelta,
        cumulativeExposure = r.cumulativeExposure,
    )

    fun scenario(s: StressManager.ScenarioResult) = StressTestScenarioResult(
        scenarioId = s.scenario.id,
        scenarioName = s.scenario.name,
        rows = s.rows.map(::row),
    )

    fun result(r: StressManager.Result) = StressTestResult(
        sessionId = r.sessionId,
        dimension = ApiDimensionKind.valueOf(r.dimension.name),
        role = ApiClientRole.valueOf(r.role.name),
        computedAt = r.computedAt.atOffset(ZoneOffset.UTC),
        scenarios = r.scenarios.map(::scenario),
    )
}
