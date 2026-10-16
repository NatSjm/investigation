package com.acme.harbor.api

import com.acme.harbor.api.generated.ClientsApi
import com.acme.harbor.api.generated.model.Client
import com.acme.harbor.api.generated.model.ClientOverview
import com.acme.harbor.api.generated.model.ClientRoleInfo
import com.acme.harbor.api.generated.model.ClientSummary
import com.acme.harbor.manager.ClientManager
import com.acme.harbor.mapper.ClientMapper
import com.acme.harbor.mapper.ClientMapper.toDomain
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import com.acme.harbor.api.generated.model.ProductGroup as ApiProductGroup

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
