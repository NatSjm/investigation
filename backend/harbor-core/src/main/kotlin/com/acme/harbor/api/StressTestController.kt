package com.acme.harbor.api

import com.acme.harbor.api.generated.StressApi
import com.acme.harbor.api.generated.model.StressTestResultDto
import com.acme.harbor.context.SessionContext
import com.acme.harbor.manager.StressManager
import com.acme.harbor.mapper.StressMapper
import com.acme.harbor.mapper.StressMapper.toDomain
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import com.acme.harbor.api.generated.model.DimensionKindDto as ApiDimensionKind
/**
 * REST adapter for the `stress` tag (session-scoped). Mappings are on the generated [StressApi];
 * the session is read from `SessionContext.current()` bound by `SessionHeaderFilter`.
 */
@RestController
class StressTestController(private val manager: StressManager) : StressApi {

    override fun runStressTest(xHarborSession: UUID): ResponseEntity<StressTestResultDto> =
        ResponseEntity.ok(StressMapper.result(manager.run(SessionContext.current())))

    override fun getStressTest(xHarborSession: UUID, dimension: ApiDimensionKind?): ResponseEntity<StressTestResultDto> =
        ResponseEntity.ok(StressMapper.result(manager.get(SessionContext.current(), dimension?.toDomain())))
}
