package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.ClientDto
import com.acme.harbor.api.generated.model.ClientOverviewDto
import com.acme.harbor.api.generated.model.ClientRoleInfoDto
import com.acme.harbor.api.generated.model.ClientSummaryDto
import com.acme.harbor.api.generated.model.ProductGroupIndicatorsDto
import com.acme.harbor.api.generated.model.RoleDecisionDto
import com.acme.harbor.api.generated.model.SparklinePointDto
import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.manager.ClientManager
import com.acme.harbor.model.ClientOverviewIndicators
import com.acme.harbor.dao.model.ClientProfile
import com.acme.harbor.dao.model.ClientRoleDecision
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.ClientRoleDto as ApiClientRole
import com.acme.harbor.api.generated.model.ProductGroupDto as ApiProductGroup
/** Maps clients, overview indicators and role decisions to the generated API models (`com.acme.harbor.api.generated.model`). */
object ClientMapper {

    fun ProductGroup.toApi(): ApiProductGroup = ApiProductGroup.valueOf(wireValue)

    fun ApiProductGroup.toDomain(): ProductGroup = ProductGroup.fromWire(value)

    fun ClientRole.toApi(): ApiClientRole = ApiClientRole.valueOf(name)

    fun summary(profile: ClientProfile, roles: List<ClientRoleDecision> = emptyList()): ClientSummaryDto = ClientSummaryDto(
        clientId = profile.id,
        externalRef = profile.externalRef,
        name = profile.name,
        country = profile.country,
        segment = profile.segment,
        productGroups = roles.map { it.productGroup }.distinct().map { it.toApi() },
    )

    fun client(view: ClientManager.ClientView): ClientDto = ClientDto(
        clientId = view.profile.id,
        externalRef = view.profile.externalRef,
        name = view.profile.name,
        country = view.profile.country,
        segment = view.profile.segment,
        productGroups = view.roles.map { it.productGroup }.distinct().map { it.toApi() },
        createdAt = view.profile.createdAt.atOffset(ZoneOffset.UTC),
        roles = view.roles.map(::decision),
    )

    fun decision(d: ClientRoleDecision): RoleDecisionDto = RoleDecisionDto(
        productGroup = d.productGroup.toApi(),
        role = d.role.toApi(),
        source = RoleDecisionDto.Source.valueOf(d.source.name),
        reason = d.reason,
        decidedAt = d.decidedAt.atOffset(ZoneOffset.UTC),
    )

    fun indicators(i: ClientOverviewIndicators): ProductGroupIndicatorsDto = ProductGroupIndicatorsDto(
        productGroup = i.productGroup.toApi(),
        volume12m = i.volume12m,
        value12m = i.value12m,
        role = i.role.toApi(),
        coverRatio = i.coverRatio,
        openSessions = i.openSessions,
        sparkline = i.sparkline.map { (period, value) -> SparklinePointDto(period = period.toString(), value = value) },
    )

    fun overview(o: ClientManager.Overview): ClientOverviewDto =
        ClientOverviewDto(client = client(o.client), productGroups = o.productGroups.map(::indicators))

    fun roleInfo(r: ClientManager.RoleView): ClientRoleInfoDto = ClientRoleInfoDto(
        clientId = r.clientId,
        productGroup = r.productGroup.toApi(),
        algorithm = decision(r.algorithm.decision),
        inboundQuantity = r.algorithm.result.inbound,
        outboundQuantity = r.algorithm.result.outbound,
        history = r.history.map(::decision),
    )
}
