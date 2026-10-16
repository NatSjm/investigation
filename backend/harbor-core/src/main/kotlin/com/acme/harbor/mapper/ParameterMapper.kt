package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.ParameterUpsertDto
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.manager.AdminManager
import com.acme.harbor.dao.model.Parameter
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.ParameterDto as ApiParameter
import com.acme.harbor.api.generated.model.ProductGroupDto as ApiProductGroup
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

    fun change(u: ParameterUpsertDto) = AdminManager.ParameterChange(
        scopeProductGroup = u.scopeProductGroup?.toDomain(),
        scopeCountry = u.scopeCountry,
        scopeValue = u.scopeValue,
        value = u.value,
        validFrom = u.validFrom,
    )
}
