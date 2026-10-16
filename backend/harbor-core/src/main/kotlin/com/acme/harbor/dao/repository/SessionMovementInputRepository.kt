package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.SessionMovementInput
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.stereotype.Repository
import java.util.UUID

/** Modelled movements entered in the movement modal (table `session_movement_input`). */
@Repository
interface SessionMovementInputRepository : JpaRepository<SessionMovementInput, UUID> {

    fun findAllBySessionIdOrderByPeriod(sessionId: UUID): List<SessionMovementInput>

    @Modifying
    fun deleteAllBySessionId(sessionId: UUID): Int
}
