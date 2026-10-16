package com.acme.harbor.api

import com.acme.harbor.api.generated.ClientsApi
import com.acme.harbor.api.generated.model.ClientDto
import com.acme.harbor.api.generated.model.ClientOverviewDto
import com.acme.harbor.api.generated.model.ClientRoleInfoDto
import com.acme.harbor.api.generated.model.ClientSummaryDto
import com.acme.harbor.manager.ClientManager
import com.acme.harbor.mapper.ClientMapper
import com.acme.harbor.mapper.ClientMapper.toDomain
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import com.acme.harbor.api.generated.model.ProductGroupDto as ApiProductGroup
/**
 * REST adapter for the `clients` tag. Request mappings live on the generated [ClientsApi] interface
 * (openapi-generator, `openapi/openapi_harbor.yaml`); this class only implements the operations.
 */
@RestController
class ClientController(private val manager: ClientManager) : ClientsApi {

    override fun searchClients(q: String): ResponseEntity<List<ClientSummaryDto>> =
        ResponseEntity.ok(manager.search(q).map { ClientMapper.summary(it) })

    override fun getClient(clientId: UUID): ResponseEntity<ClientDto> =
        ResponseEntity.ok(ClientMapper.client(manager.get(clientId)))

    override fun getClientOverview(clientId: UUID): ResponseEntity<ClientOverviewDto> =
        ResponseEntity.ok(ClientMapper.overview(manager.overview(clientId)))

    override fun getClientRole(clientId: UUID, productGroup: ApiProductGroup): ResponseEntity<ClientRoleInfoDto> =
        ResponseEntity.ok(ClientMapper.roleInfo(manager.role(clientId, productGroup.toDomain())))
}
