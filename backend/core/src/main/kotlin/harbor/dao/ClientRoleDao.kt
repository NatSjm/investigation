package harbor.dao

import harbor.enums.ProductGroup
import harbor.model.ClientRoleDecision
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Append-only role decisions per client and product group (table `client_role`). */
@Repository
interface ClientRoleDao : JpaRepository<ClientRoleDecision, Long> {

    fun findFirstByClientIdAndProductGroupOrderByDecidedAtDesc(clientId: UUID, productGroup: ProductGroup): ClientRoleDecision?

    fun findAllByClientIdAndProductGroupOrderByDecidedAtDesc(clientId: UUID, productGroup: ProductGroup): List<ClientRoleDecision>

    fun findAllByClientId(clientId: UUID): List<ClientRoleDecision>
}
