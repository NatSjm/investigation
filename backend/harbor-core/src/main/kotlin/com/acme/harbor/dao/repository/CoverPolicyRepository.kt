package com.acme.harbor.dao.repository

import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.dao.model.CoverPolicy
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Cover policies of the clients (table `cover_policy`). */
@Repository
interface CoverPolicyRepository : JpaRepository<CoverPolicy, UUID> {

    fun findAllByClientIdOrderByValidFromDesc(clientId: UUID): List<CoverPolicy>

    fun findAllByClientIdAndProductGroup(clientId: UUID, productGroup: ProductGroup): List<CoverPolicy>
}
