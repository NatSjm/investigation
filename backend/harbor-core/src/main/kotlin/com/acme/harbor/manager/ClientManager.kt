package com.acme.harbor.manager

import com.acme.harbor.dao.repository.ClientRoleRepository
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.model.ClientOverviewIndicators
import com.acme.harbor.dao.model.ClientProfile
import com.acme.harbor.dao.model.ClientRoleDecision
import com.acme.harbor.service.ClientOverviewService
import com.acme.harbor.service.ClientProfileService
import com.acme.harbor.service.ClientRoleService
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.util.UUID

/**
 * Client search, profile, overview indicators and role classification.
 *
 * Search goes to the external client-registry and merges the local `client_profile` rows; a profile is
 * created lazily the first time a registry entry is opened ([ClientProfileService]). The overview per product
 * group is assembled by [ClientOverviewService] from the role (`client_role_classification`), the actual
 * movements, the cover ratio and the open sessions.
 *
 * @docs CLI-001
 */
@Service
class ClientManager(
    private val profileService: ClientProfileService,
    private val roleRepository: ClientRoleRepository,
    private val roleService: ClientRoleService,
    private val overviewService: ClientOverviewService,
) {

    data class ClientView(val profile: ClientProfile, val roles: List<ClientRoleDecision>)

    data class Overview(val client: ClientView, val productGroups: List<ClientOverviewIndicators>)

    data class RoleView(
        val clientId: UUID,
        val productGroup: ProductGroup,
        val algorithm: ClientRoleService.Classification,
        val history: List<ClientRoleDecision>,
    )

    fun search(query: String): List<ClientProfile> = profileService.search(query)

    @Transactional(readOnly = true)
    fun get(clientId: UUID): ClientView {
        val profile = profileService.get(clientId)
        return ClientView(profile, roleRepository.findAllByClientId(clientId).sortedByDescending { it.decidedAt })
    }

    @Transactional
    fun overview(clientId: UUID): Overview = Overview(get(clientId), overviewService.indicators(clientId))

    @Transactional
    fun role(clientId: UUID, productGroup: ProductGroup): RoleView {
        profileService.get(clientId)
        return RoleView(
            clientId = clientId,
            productGroup = productGroup,
            algorithm = roleService.classifyAndRecord(clientId, productGroup),
            history = roleService.history(clientId, productGroup),
        )
    }
}
