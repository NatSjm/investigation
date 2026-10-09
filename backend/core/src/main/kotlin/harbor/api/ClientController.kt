package harbor.api

import harbor.api.generated.ClientsApi
import harbor.api.generated.model.Client
import harbor.api.generated.model.ClientOverview
import harbor.api.generated.model.ClientRoleInfo
import harbor.api.generated.model.ClientSummary
import harbor.manager.ClientManager
import harbor.mapper.ClientMapper
import harbor.mapper.ClientMapper.toDomain
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import harbor.api.generated.model.ProductGroup as ApiProductGroup

/**
 * REST adapter for the `clients` tag. Request mappings live on the generated [ClientsApi] interface
 * (openapi-generator, `openapi/harbor-api.yaml`); this class only implements the operations.
 */
@RestController
class ClientController(private val manager: ClientManager) : ClientsApi {

    override fun searchClients(q: String): ResponseEntity<List<ClientSummary>> =
        ResponseEntity.ok(manager.search(q).map { ClientMapper.summary(it) })

    override fun getClient(clientId: UUID): ResponseEntity<Client> =
        ResponseEntity.ok(ClientMapper.client(manager.get(clientId)))

    override fun getClientOverview(clientId: UUID): ResponseEntity<ClientOverview> =
        ResponseEntity.ok(ClientMapper.overview(manager.overview(clientId)))

    override fun getClientRole(clientId: UUID, productGroup: ApiProductGroup): ResponseEntity<ClientRoleInfo> =
        ResponseEntity.ok(ClientMapper.roleInfo(manager.role(clientId, productGroup.toDomain())))
}
