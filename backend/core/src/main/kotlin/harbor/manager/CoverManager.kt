package harbor.manager

import harbor.context.SessionScope
import harbor.dao.CoverPolicyDao
import harbor.model.CoverPolicy
import harbor.model.CoverQuote
import harbor.service.ClientProfileService
import harbor.service.CoverQuoteService
import harbor.service.CoverRatioService
import harbor.service.ProjectionService
import harbor.utils.CoverRatioCalculator
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.util.UUID

/**
 * Cover of the current session: cover ratio per month and sub-product (`cover_ratio` on top of the
 * projection's value by sub-product), the uncovered value, and quotes for the uncovered part requested
 * from the external cover-provider and stored in `cover_quote`. Policies of a client are listed outside
 * the session scope.
 *
 * @docs COV-001
 */
@Service
class CoverManager(
    private val policyDao: CoverPolicyDao,
    private val projectionService: ProjectionService,
    private val coverRatioService: CoverRatioService,
    private val quoteService: CoverQuoteService,
    private val clientProfiles: ClientProfileService,
) {

    data class Summary(val sessionId: UUID, val months: List<CoverRatioCalculator.CoverMonth>, val uncoveredValue: BigDecimal)

    @Transactional
    fun summary(scope: SessionScope): Summary {
        val cover = coverRatioService.cover(scope, projectionService.loadOrCompute(scope))
        return Summary(scope.sessionId, cover.perMonth + cover.perSubProduct, cover.uncoveredValue)
    }

    @Transactional
    fun requestQuote(scope: SessionScope, request: CoverQuoteService.QuoteRequest): CoverQuote {
        val tables = projectionService.loadOrCompute(scope)
        val from = request.fromPeriod ?: tables.summary.first().period
        val to = request.toPeriod ?: tables.summary.last().period
        require(!to.isBefore(from)) { "toPeriod must not be before fromPeriod" }
        val uncovered = coverRatioService.cover(scope, tables, request.subProducts, from, to).uncoveredValue
        val clientRef = clientProfiles.get(scope.clientId).externalRef
        return quoteService.requestQuote(scope, clientRef, request, uncovered, from, to)
    }

    @Transactional(readOnly = true)
    fun policies(clientId: UUID): List<CoverPolicy> {
        clientProfiles.get(clientId)
        return policyDao.findAllByClientIdOrderByValidFromDesc(clientId)
    }
}
