package com.acme.harbor.dao.model

import com.acme.harbor.enums.Direction
import com.acme.harbor.enums.TransportMode
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

/**
 * A modelled movement entered per month in the movement modal (table `session_movement_input`,
 * V4__session_inputs.sql). For a month with modelled inputs these rows replace the carried-forward
 * actual movements in the projection. Shared by Product 1 and Product 2 sessions.
 */
@Entity
@Table(name = "session_movement_input")
class SessionMovementInput(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "session_id", nullable = false)
    val sessionId: UUID,

    @Column(name = "period", nullable = false)
    val period: LocalDate,

    @Column(name = "sub_product", nullable = false)
    val subProduct: String,

    @Column(name = "city")
    val city: String?,

    @Enumerated(EnumType.STRING)
    @Column(name = "transport_mode")
    val transportMode: TransportMode?,

    @Enumerated(EnumType.STRING)
    @Column(name = "direction", nullable = false)
    val direction: Direction,

    @Column(name = "quantity", nullable = false)
    val quantity: BigDecimal,

    @Column(name = "unit_price", nullable = false)
    val unitPrice: BigDecimal,
)
