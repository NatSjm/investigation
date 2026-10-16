package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.CoverMonthDto
import com.acme.harbor.api.generated.model.CoverQuoteDto
import com.acme.harbor.api.generated.model.CoverQuoteRequestDto
import com.acme.harbor.api.generated.model.CoverSummaryDto
import com.acme.harbor.manager.CoverManager
import com.acme.harbor.dao.model.CoverPolicy
import com.acme.harbor.service.CoverQuoteService
import java.time.YearMonth
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.CoverPolicyDto as ApiCoverPolicy
import com.acme.harbor.api.generated.model.ProductGroupDto as ApiProductGroup
import com.acme.harbor.dao.model.CoverQuote as CoverQuoteEntity
import com.acme.harbor.utils.CoverRatioCalculator.CoverMonth as CalcCoverMonth

/** Maps cover summaries, quotes and policies to the generated API models. */
object CoverMapper {

    fun month(m: CalcCoverMonth) = CoverMonthDto(
        period = m.period.toString(),
        subProduct = m.subProduct,
        totalValue = m.totalValue,
        coveredValue = m.coveredValue,
        coverRatio = m.coverRatio,
    )

    fun summary(s: CoverManager.Summary) =
        CoverSummaryDto(sessionId = s.sessionId, months = s.months.map(::month), uncoveredValue = s.uncoveredValue)

    fun quoteRequest(r: CoverQuoteRequestDto) = CoverQuoteService.QuoteRequest(
        subProducts = r.subProducts,
        targetCoveredShare = r.targetCoveredShare,
        fromPeriod = r.fromPeriod?.let(YearMonth::parse),
        toPeriod = r.toPeriod?.let(YearMonth::parse),
    )

    fun quote(q: CoverQuoteEntity) = CoverQuoteDto(
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
