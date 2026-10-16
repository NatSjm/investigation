package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.MarketScenario
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Market scenarios per session (table `market_scenario`). */
@Repository
interface MarketScenarioRepository : JpaRepository<MarketScenario, UUID> {

    fun findAllBySessionIdOrderByCreatedAt(sessionId: UUID): List<MarketScenario>

    fun findByIdAndSessionId(id: UUID, sessionId: UUID): MarketScenario?

    fun countBySessionId(sessionId: UUID): Int
}
