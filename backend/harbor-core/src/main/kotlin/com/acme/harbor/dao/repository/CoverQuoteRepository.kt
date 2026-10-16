package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.CoverQuote
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Quotes obtained from cover-provider per session (table `cover_quote`). */
@Repository
interface CoverQuoteRepository : JpaRepository<CoverQuote, UUID> {

    fun findAllBySessionIdOrderByRequestedAtDesc(sessionId: UUID): List<CoverQuote>
}
