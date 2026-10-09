package harbor.service

import harbor.client.CoverProviderClient
import harbor.context.SessionScope
import harbor.dao.CoverQuoteDao
import harbor.enums.ParameterKey
import harbor.model.CoverQuote
import harbor.utils.Rounding
import harbor.utils.money
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.Clock
import java.time.Instant
import java.time.YearMonth

/**
 * Quotes for the uncovered value of a session: asks the external cover-provider and stores the answer in
 * `cover_quote`. When the provider is unavailable the premium falls back to `cover.default_premium_rate`
 * so the meeting can continue.
 */
@Service
class CoverQuoteService(
    private val quoteDao: CoverQuoteDao,
    private val provider: CoverProviderClient,
    private val parameters: ParameterService,
    private val clock: Clock,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    data class QuoteRequest(val subProducts: List<String>, val targetCoveredShare: BigDecimal?, val fromPeriod: YearMonth?, val toPeriod: YearMonth?)

    @Transactional
    fun requestQuote(
        scope: SessionScope,
        clientRef: String,
        request: QuoteRequest,
        uncoveredValue: BigDecimal,
        from: YearMonth,
        to: YearMonth,
    ): CoverQuote {
        require(uncoveredValue.signum() > 0) { "Nothing to quote: the selected sub-products are fully covered" }
        val quote = runCatching {
            provider.requestQuote(clientRef, scope.productGroup, request.subProducts, uncoveredValue, request.targetCoveredShare, from, to)
        }.getOrElse { e ->
            log.warn("cover-provider unavailable for session {}, using cover.default_premium_rate", scope.sessionId, e)
            val rate = parameters.required(ParameterKey.COVER_DEFAULT_PREMIUM_RATE)
            CoverProviderClient.Quote(providerRef = "", premium = (uncoveredValue * rate).money(), premiumRate = rate, validUntil = Instant.now(clock))
        }
        return quoteDao.save(
            CoverQuote(
                sessionId = scope.sessionId,
                requestedAt = Instant.now(clock),
                uncoveredValue = uncoveredValue.setScale(Rounding.MONEY_SCALE, Rounding.MODE),
                premium = quote.premium,
                providerRef = quote.providerRef.ifEmpty { null },
            ),
        )
    }

    fun quotes(scope: SessionScope): List<CoverQuote> = quoteDao.findAllBySessionIdOrderByRequestedAtDesc(scope.sessionId)
}
