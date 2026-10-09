package harbor.mapper

import harbor.api.generated.model.ParameterUpsert
import harbor.enums.ProductGroup
import harbor.manager.AdminManager
import harbor.model.Parameter
import java.time.ZoneOffset
import harbor.api.generated.model.Parameter as ApiParameter
import harbor.api.generated.model.ProductGroup as ApiProductGroup

/** Maps parameter values and the upsert request body to / from the generated API models. */
object ParameterMapper {

    fun ApiProductGroup.toDomain(): ProductGroup = ProductGroup.fromWire(value)

    fun parameter(p: Parameter) = ApiParameter(
        parameterId = p.id,
        key = p.key,
        scopeProductGroup = p.scopeProductGroup?.let { ApiProductGroup.valueOf(it.wireValue) },
        scopeCountry = p.scopeCountry,
        scopeValue = p.scopeValue,
        value = p.value,
        validFrom = p.validFrom,
        updatedBy = p.updatedBy,
        updatedAt = p.updatedAt.atOffset(ZoneOffset.UTC),
    )

    fun change(u: ParameterUpsert) = AdminManager.ParameterChange(
        scopeProductGroup = u.scopeProductGroup?.toDomain(),
        scopeCountry = u.scopeCountry,
        scopeValue = u.scopeValue,
        value = u.value,
        validFrom = u.validFrom,
    )
}
