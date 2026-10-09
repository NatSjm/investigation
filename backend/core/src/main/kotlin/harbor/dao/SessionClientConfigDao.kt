package harbor.dao

import harbor.model.SessionClientConfig
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Per-session client configuration, keyed by session id (table `session_client_config`). */
@Repository
interface SessionClientConfigDao : JpaRepository<SessionClientConfig, UUID>
