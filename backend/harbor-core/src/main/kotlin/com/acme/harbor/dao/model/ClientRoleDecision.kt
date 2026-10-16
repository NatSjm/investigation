package com.acme.harbor.dao.model

import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.enums.RoleSource
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.time.Instant
import java.util.UUID

/**
 * One role decision for a client and product group (table `client_role`, V1__clients.sql).
 * Rows are append-only: the newest row per (client, product group) is the current role, the older rows are
 * the history shown on the client overview.
 */
@Entity
@Table(name = "client_role")
class ClientRoleDecision(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    val id: Long? = null,

    @Column(name = "client_id", nullable = false)
    val clientId: UUID,

    @Enumerated(EnumType.STRING)
    @Column(name = "product_group", nullable = false)
    val productGroup: ProductGroup,

    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false)
    val role: ClientRole,

    @Enumerated(EnumType.STRING)
    @Column(name = "source", nullable = false)
    val source: RoleSource,

    @Column(name = "reason")
    val reason: String? = null,

    @Column(name = "decided_at", nullable = false)
    val decidedAt: Instant = Instant.now(),
)
