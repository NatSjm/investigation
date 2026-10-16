package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.SessionPeerSimulation
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Runs of the peer simulation modal (table `session_peer_simulation`). */
@Repository
interface SessionPeerSimulationRepository : JpaRepository<SessionPeerSimulation, UUID> {

    fun findFirstBySessionIdOrderByGeneratedAtDesc(sessionId: UUID): SessionPeerSimulation?
}
