package harbor.mapper

import harbor.api.generated.model.CoverMonth
import harbor.api.generated.model.CoverQuote
import harbor.api.generated.model.CoverQuoteRequest
import harbor.api.generated.model.CoverSummary
import harbor.manager.CoverManager
import harbor.model.CoverPolicy
import harbor.service.CoverQuoteService
import java.time.YearMonth
import java.time.ZoneOffset
import harbor.api.generated.model.CoverPolicy as ApiCoverPolicy
import harbor.api.generated.model.ProductGroup as ApiProductGroup
import harbor.model.CoverQuote as CoverQuoteEntity
import harbor.utils.CoverRatioCalculator.CoverMonth as CalcCoverMonth

/** Maps cover summaries, quotes and policies to the generated API models. */
object CoverMapper {

    fun month(m: CalcCoverMonth) = CoverMonth(
        period = m.period.toString(),
        subProduct = m.subProduct,
        totalValue = m.totalValue,
        coveredValue = m.coveredValue,
        coverRatio = m.coverRatio,
    )

    fun summary(s: CoverManager.Summary) =
        CoverSummary(sessionId = s.sessionId, months = s.months.map(::month), uncoveredValue = s.uncoveredValue)

    fun quoteRequest(r: CoverQuoteRequest) = CoverQuoteService.QuoteRequest(
        subProducts = r.subProducts,
        targetCoveredShare = r.targetCoveredShare,
        fromPeriod = r.fromPeriod?.let(YearMonth::parse),
        toPeriod = r.toPeriod?.let(YearMonth::parse),
    )

    fun quote(q: CoverQuoteEntity) = CoverQuote(
        quoteId = q.id,
        sessionId = q.sessionId,
        requestedAt = q.requestedAt.atOffset(ZoneOffset.UTC),
        uncoveredValue = q.uncoveredValue,
        premium = q.premium,
        providerRef = q.providerRef,
    )

    fun policy(p: CoverPolicy) = ApiCoverPolicy(
        policyId = p.id,
        clientId = p.clientId,
        productGroup = ApiProductGroup.valueOf(p.productGroup.wireValue),
        subProduct = p.subProduct,
        coveredShare = p.coveredShare,
        premiumRate = p.premiumRate,
        validFrom = p.validFrom,
        validTo = p.validTo,
    )
}
