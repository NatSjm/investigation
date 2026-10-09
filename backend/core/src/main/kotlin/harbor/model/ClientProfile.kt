package harbor.model

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.time.Instant
import java.util.UUID

/**
 * Local profile of a client (table `client_profile`, V1__clients.sql). Master data comes from the
 * client-registry service; the profile is created on first use and keyed by the registry's `external_ref`.
 */
@Entity
@Table(name = "client_profile")
class ClientProfile(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "external_ref", nullable = false, unique = true)
    val externalRef: String,

    @Column(name = "name", nullable = false)
    var name: String,

    @Column(name = "country")
    var country: String? = null,

    @Column(name = "segment")
    var segment: String? = null,

    @Column(name = "created_at", nullable = false)
    val createdAt: Instant = Instant.now(),
)
