package harbor.dao

import harbor.model.SessionPeerSimulation
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Runs of the peer simulation modal (table `session_peer_simulation`). */
@Repository
interface SessionPeerSimulationDao : JpaRepository<SessionPeerSimulation, UUID> {

    fun findFirstBySessionIdOrderByGeneratedAtDesc(sessionId: UUID): SessionPeerSimulation?
}
