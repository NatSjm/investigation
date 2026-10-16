package com.acme.harbor.api

import com.acme.harbor.api.generated.CoverApi
import com.acme.harbor.api.generated.model.CoverPolicyDto
import com.acme.harbor.api.generated.model.CoverQuoteDto
import com.acme.harbor.api.generated.model.CoverQuoteRequestDto
import com.acme.harbor.api.generated.model.CoverSummaryDto
import com.acme.harbor.context.SessionContext
import com.acme.harbor.manager.CoverManager
import com.acme.harbor.mapper.CoverMapper
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RestController
import java.util.UUID

/**
 * REST adapter for the `cover` tag. `getCoverSummary` and `requestCoverQuote` are session-scoped
 * (`SessionContext.current()`); `listCoverPolicies` is keyed by client id.
 */
@RestController
class CoverController(private val manager: CoverManager) : CoverApi {

    override fun getCoverSummary(xHarborSession: UUID): ResponseEntity<CoverSummaryDto> =
        ResponseEntity.ok(CoverMapper.summary(manager.summary(SessionContext.current())))

    override fun requestCoverQuote(xHarborSession: UUID, coverQuoteRequest: CoverQuoteRequestDto): ResponseEntity<CoverQuoteDto> {
        val quote = manager.requestQuote(SessionContext.current(), CoverMapper.quoteRequest(coverQuoteRequest))
        return ResponseEntity.status(HttpStatus.CREATED).body(CoverMapper.quote(quote))
    }

    override fun listCoverPolicies(clientId: UUID): ResponseEntity<List<CoverPolicyDto>> =
        ResponseEntity.ok(manager.policies(clientId).map(CoverMapper::policy))
}
