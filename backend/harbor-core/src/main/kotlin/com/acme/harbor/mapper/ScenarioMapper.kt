package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.BaselinePricePoint
import com.acme.harbor.api.generated.model.BaselinePrices
import com.acme.harbor.api.generated.model.Scenario
import com.acme.harbor.api.generated.model.ScenarioInput
import com.acme.harbor.api.generated.model.Shock
import com.acme.harbor.enums.ScenarioKind
import com.acme.harbor.dao.model.MarketScenario
import com.acme.harbor.model.ScenarioShock
import com.acme.harbor.service.BaselinePriceService
import com.acme.harbor.service.ScenarioService
import com.acme.harbor.utils.money
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.ProductGroup as ApiProductGroup

/** Maps scenarios and baseline curves to the generated API models. */
object ScenarioMapper {

    fun input(api: ScenarioInput): ScenarioService.ScenarioInput = ScenarioService.ScenarioInput(
        name = api.name,
        kind = ScenarioKind.valueOf(api.kind.name),
        shocks = api.shocks.map { ScenarioShock(it.fromMonth, it.priceChangePct, it.transportChangePct) },
    )

    fun scenario(s: MarketScenario): Scenario = Scenario(
        name = s.name,
        kind = Scenario.Kind.valueOf(s.kind.name),
        shocks = s.shocks.map { Shock(fromMonth = it.fromMonth, priceChangePct = it.priceChangePct, transportChangePct = it.transportChangePct) },
        scenarioId = s.id,
        sessionId = s.sessionId,
        createdBy = s.createdBy,
        createdAt = s.createdAt.atOffset(ZoneOffset.UTC),
    )

    fun baseline(curve: BaselinePriceService.Curve): BaselinePrices = BaselinePrices(
        productGroup = ApiProductGroup.valueOf(curve.productGroup.wireValue),
        corridor = curve.productGroup.corridor,
        asOf = curve.asOf.atOffset(ZoneOffset.UTC),
        points = curve.points.entries.sortedBy { it.key }.map { (month, point) ->
            BaselinePricePoint(period = month.toString(), price = point.price.money(), transportPrice = point.transportPrice.money())
        },
    )
}
