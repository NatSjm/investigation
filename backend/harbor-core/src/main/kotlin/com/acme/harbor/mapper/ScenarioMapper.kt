package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.BaselinePricePointDto
import com.acme.harbor.api.generated.model.BaselinePricesDto
import com.acme.harbor.api.generated.model.ScenarioDto
import com.acme.harbor.api.generated.model.ScenarioInputDto
import com.acme.harbor.api.generated.model.ShockDto
import com.acme.harbor.enums.ScenarioKind
import com.acme.harbor.dao.model.MarketScenario
import com.acme.harbor.model.ScenarioShock
import com.acme.harbor.service.BaselinePriceService
import com.acme.harbor.service.ScenarioService
import com.acme.harbor.utils.money
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.ProductGroupDto as ApiProductGroup
/** Maps scenarios and baseline curves to the generated API models. */
object ScenarioMapper {

    fun input(api: ScenarioInputDto): ScenarioService.ScenarioInput = ScenarioService.ScenarioInput(
        name = api.name,
        kind = ScenarioKind.valueOf(api.kind.name),
        shocks = api.shocks.map { ScenarioShock(it.fromMonth, it.priceChangePct, it.transportChangePct) },
    )

    fun scenario(s: MarketScenario): ScenarioDto = ScenarioDto(
        name = s.name,
        kind = ScenarioDto.Kind.valueOf(s.kind.name),
        shocks = s.shocks.map { ShockDto(fromMonth = it.fromMonth, priceChangePct = it.priceChangePct, transportChangePct = it.transportChangePct) },
        scenarioId = s.id,
        sessionId = s.sessionId,
        createdBy = s.createdBy,
        createdAt = s.createdAt.atOffset(ZoneOffset.UTC),
    )

    fun baseline(curve: BaselinePriceService.Curve): BaselinePricesDto = BaselinePricesDto(
        productGroup = ApiProductGroup.valueOf(curve.productGroup.wireValue),
        corridor = curve.productGroup.corridor,
        asOf = curve.asOf.atOffset(ZoneOffset.UTC),
        points = curve.points.entries.sortedBy { it.key }.map { (month, point) ->
            BaselinePricePointDto(period = month.toString(), price = point.price.money(), transportPrice = point.transportPrice.money())
        },
    )
}
