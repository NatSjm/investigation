package harbor.mapper

import harbor.api.generated.model.Client
import harbor.api.generated.model.ClientOverview
import harbor.api.generated.model.ClientRoleInfo
import harbor.api.generated.model.ClientSummary
import harbor.api.generated.model.ProductGroupIndicators
import harbor.api.generated.model.RoleDecision
import harbor.api.generated.model.SparklinePoint
import harbor.enums.ClientRole
import harbor.enums.ProductGroup
import harbor.manager.ClientManager
import harbor.model.ClientOverviewIndicators
import harbor.model.ClientProfile
import harbor.model.ClientRoleDecision
import java.time.ZoneOffset
import harbor.api.generated.model.ClientRole as ApiClientRole
import harbor.api.generated.model.ProductGroup as ApiProductGroup

/** Maps clients, overview indicators and role decisions to the generated API models (`harbor.api.generated.model`). */
object ClientMapper {

    fun ProductGroup.toApi(): ApiProductGroup = ApiProductGroup.valueOf(wireValue)

    fun ApiProductGroup.toDomain(): ProductGroup = ProductGroup.fromWire(value)

    fun ClientRole.toApi(): ApiClientRole = ApiClientRole.valueOf(name)

    fun summary(profile: ClientProfile, roles: List<ClientRoleDecision> = emptyList()): ClientSummary = ClientSummary(
        clientId = profile.id,
        externalRef = profile.externalRef,
        name = profile.name,
        country = profile.country,
        segment = profile.segment,
        productGroups = roles.map { it.productGroup }.distinct().map { it.toApi() },
    )

    fun client(view: ClientManager.ClientView): Client = Client(
        clientId = view.profile.id,
        externalRef = view.profile.externalRef,
        name = view.profile.name,
        country = view.profile.country,
        segment = view.profile.segment,
        productGroups = view.roles.map { it.productGroup }.distinct().map { it.toApi() },
        createdAt = view.profile.createdAt.atOffset(ZoneOffset.UTC),
        roles = view.roles.map(::decision),
    )

    fun decision(d: ClientRoleDecision): RoleDecision = RoleDecision(
        productGroup = d.productGroup.toApi(),
        role = d.role.toApi(),
        source = RoleDecision.Source.valueOf(d.source.name),
        reason = d.reason,
        decidedAt = d.decidedAt.atOffset(ZoneOffset.UTC),
    )

    fun indicators(i: ClientOverviewIndicators): ProductGroupIndicators = ProductGroupIndicators(
        productGroup = i.productGroup.toApi(),
        volume12m = i.volume12m,
        value12m = i.value12m,
        role = i.role.toApi(),
        coverRatio = i.coverRatio,
        openSessions = i.openSessions,
        sparkline = i.sparkline.map { (period, value) -> SparklinePoint(period = period.toString(), value = value) },
    )

    fun overview(o: ClientManager.Overview): ClientOverview =
        ClientOverview(client = client(o.client), productGroups = o.productGroups.map(::indicators))

    fun roleInfo(r: ClientManager.RoleView): ClientRoleInfo = ClientRoleInfo(
        clientId = r.clientId,
        productGroup = r.productGroup.toApi(),
        algorithm = decision(r.algorithm.decision),
        inboundQuantity = r.algorithm.result.inbound,
        outboundQuantity = r.algorithm.result.outbound,
        history = r.history.map(::decision),
    )
}
