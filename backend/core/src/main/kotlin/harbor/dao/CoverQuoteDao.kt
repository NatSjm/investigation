package harbor.dao

import harbor.model.CoverQuote
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Quotes obtained from cover-provider per session (table `cover_quote`). */
@Repository
interface CoverQuoteDao : JpaRepository<CoverQuote, UUID> {

    fun findAllBySessionIdOrderByRequestedAtDesc(sessionId: UUID): List<CoverQuote>
}
