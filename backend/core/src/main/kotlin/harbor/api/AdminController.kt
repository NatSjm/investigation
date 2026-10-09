package harbor.api

import harbor.api.generated.AdminApi
import harbor.api.generated.model.ImportBatch
import harbor.api.generated.model.Parameter
import harbor.api.generated.model.ParameterUpsert
import harbor.manager.AdminManager
import harbor.mapper.ImportBatchMapper
import harbor.mapper.ParameterMapper
import harbor.mapper.ParameterMapper.toDomain
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import harbor.api.generated.model.ProductGroup as ApiProductGroup

/** REST adapter for the `admin` tag. Mappings are on the generated [AdminApi]; nothing here is session-scoped. */
@RestController
class AdminController(private val manager: AdminManager) : AdminApi {

    override fun listParameters(productGroup: ApiProductGroup?): ResponseEntity<List<Parameter>> =
        ResponseEntity.ok(manager.listParameters(productGroup?.toDomain()).map(ParameterMapper::parameter))

    override fun upsertParameter(key: String, parameterUpsert: ParameterUpsert): ResponseEntity<Parameter> =
        ResponseEntity.ok(ParameterMapper.parameter(manager.upsertParameter(key, ParameterMapper.change(parameterUpsert))))

    override fun listImportBatches(): ResponseEntity<List<ImportBatch>> =
        ResponseEntity.ok(manager.listImportBatches().map(ImportBatchMapper::batch))

    override fun triggerImport(): ResponseEntity<ImportBatch> =
        ResponseEntity.status(HttpStatus.ACCEPTED).body(ImportBatchMapper.batch(manager.triggerImport()))
}
