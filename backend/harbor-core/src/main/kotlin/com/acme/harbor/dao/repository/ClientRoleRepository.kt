package com.acme.harbor.dao.repository

import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.dao.model.ClientRoleDecision
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Append-only role decisions per client and product group (table `client_role`). */
@Repository
interface ClientRoleRepository : JpaRepository<ClientRoleDecision, Long> {

    fun findFirstByClientIdAndProductGroupOrderByDecidedAtDesc(clientId: UUID, productGroup: ProductGroup): ClientRoleDecision?

    fun findAllByClientIdAndProductGroupOrderByDecidedAtDesc(clientId: UUID, productGroup: ProductGroup): List<ClientRoleDecision>

    fun findAllByClientId(clientId: UUID): List<ClientRoleDecision>
}
