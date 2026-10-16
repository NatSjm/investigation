package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.StressTestResult
import com.acme.harbor.api.generated.model.StressTestRow
import com.acme.harbor.api.generated.model.StressTestScenarioResult
import com.acme.harbor.enums.StressDimension
import com.acme.harbor.manager.StressManager
import com.acme.harbor.utils.StressTestCalculator
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.ClientRole as ApiClientRole
import com.acme.harbor.api.generated.model.DimensionKind as ApiDimensionKind

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
