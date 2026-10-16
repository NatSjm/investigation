package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.StressTestResultDto
import com.acme.harbor.api.generated.model.StressTestRowDto
import com.acme.harbor.api.generated.model.StressTestScenarioResultDto
import com.acme.harbor.enums.StressDimension
import com.acme.harbor.manager.StressManager
import com.acme.harbor.utils.StressTestCalculator
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.ClientRoleDto as ApiClientRole
import com.acme.harbor.api.generated.model.DimensionKindDto as ApiDimensionKind
/** Maps stress test results to the generated API models. */
object StressMapper {

    fun ApiDimensionKind.toDomain(): StressDimension = StressDimension.valueOf(name)

    fun row(r: StressTestCalculator.MonthResult) = StressTestRowDto(
        period = r.period.toString(),
        dimensionValue = r.dimensionValue,
        scenarioPrice = r.scenarioPrice,
        scenarioTransportPrice = r.scenarioTransportPrice,
        exposure = r.exposure,
        transportCostDelta = r.transportCostDelta,
        cumulativeExposure = r.cumulativeExposure,
    )

    fun scenario(s: StressManager.ScenarioResult) = StressTestScenarioResultDto(
        scenarioId = s.scenario.id,
        scenarioName = s.scenario.name,
        rows = s.rows.map(::row),
    )

    fun result(r: StressManager.Result) = StressTestResultDto(
        sessionId = r.sessionId,
        dimension = ApiDimensionKind.valueOf(r.dimension.name),
        role = ApiClientRole.valueOf(r.role.name),
        computedAt = r.computedAt.atOffset(ZoneOffset.UTC),
        scenarios = r.scenarios.map(::scenario),
    )
}
