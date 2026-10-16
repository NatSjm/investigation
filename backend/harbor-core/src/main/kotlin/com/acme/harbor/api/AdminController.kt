package com.acme.harbor.api

import com.acme.harbor.api.generated.AdminApi
import com.acme.harbor.api.generated.model.ImportBatchDto
import com.acme.harbor.api.generated.model.ParameterDto
import com.acme.harbor.api.generated.model.ParameterUpsertDto
import com.acme.harbor.manager.AdminManager
import com.acme.harbor.mapper.ImportBatchMapper
import com.acme.harbor.mapper.ParameterMapper
import com.acme.harbor.mapper.ParameterMapper.toDomain
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import com.acme.harbor.api.generated.model.ProductGroupDto as ApiProductGroup
/** REST adapter for the `admin` tag. Mappings are on the generated [AdminApi]; nothing here is session-scoped. */
@RestController
class AdminController(private val manager: AdminManager) : AdminApi {

    override fun listParameters(productGroup: ApiProductGroup?): ResponseEntity<List<ParameterDto>> =
        ResponseEntity.ok(manager.listParameters(productGroup?.toDomain()).map(ParameterMapper::parameter))

    override fun upsertParameter(key: String, parameterUpsert: ParameterUpsertDto): ResponseEntity<ParameterDto> =
        ResponseEntity.ok(ParameterMapper.parameter(manager.upsertParameter(key, ParameterMapper.change(parameterUpsert))))

    override fun listImportBatches(): ResponseEntity<List<ImportBatchDto>> =
        ResponseEntity.ok(manager.listImportBatches().map(ImportBatchMapper::batch))

    override fun triggerImport(): ResponseEntity<ImportBatchDto> =
        ResponseEntity.status(HttpStatus.ACCEPTED).body(ImportBatchMapper.batch(manager.triggerImport()))
}
