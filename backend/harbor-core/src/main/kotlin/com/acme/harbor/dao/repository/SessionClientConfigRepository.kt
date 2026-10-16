package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.SessionClientConfig
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** Per-session client configuration, keyed by session id (table `session_client_config`). */
@Repository
interface SessionClientConfigRepository : JpaRepository<SessionClientConfig, UUID>
