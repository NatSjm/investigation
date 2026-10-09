package harbor.mapper

import harbor.api.generated.model.BaselinePricePoint
import harbor.api.generated.model.BaselinePrices
import harbor.api.generated.model.Scenario
import harbor.api.generated.model.ScenarioInput
import harbor.api.generated.model.Shock
import harbor.enums.ScenarioKind
import harbor.model.MarketScenario
import harbor.model.ScenarioShock
import harbor.service.BaselinePriceService
import harbor.service.ScenarioService
import harbor.utils.money
import java.time.ZoneOffset
import harbor.api.generated.model.ProductGroup as ApiProductGroup

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
