package harbor.api

import harbor.api.generated.StressApi
import harbor.api.generated.model.StressTestResult
import harbor.context.SessionContext
import harbor.manager.StressManager
import harbor.mapper.StressMapper
import harbor.mapper.StressMapper.toDomain
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID
import harbor.api.generated.model.DimensionKind as ApiDimensionKind

/**
 * REST adapter for the `stress` tag (session-scoped). Mappings are on the generated [StressApi];
 * the session is read from `SessionContext.current()` bound by `SessionHeaderFilter`.
 */
@RestController
class StressTestController(private val manager: StressManager) : StressApi {

    override fun runStressTest(xHarborSession: UUID): ResponseEntity<StressTestResult> =
        ResponseEntity.ok(StressMapper.result(manager.run(SessionContext.current())))

    override fun getStressTest(xHarborSession: UUID, dimension: ApiDimensionKind?): ResponseEntity<StressTestResult> =
        ResponseEntity.ok(StressMapper.result(manager.get(SessionContext.current(), dimension?.toDomain())))
}
