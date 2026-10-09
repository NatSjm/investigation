package harbor.service

import harbor.client.ClientRegistryClient
import harbor.dao.ClientProfileDao
import harbor.exception.NotFoundException
import harbor.model.ClientProfile
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.util.UUID

/**
 * Local client profiles (`client_profile`) on top of the external client-registry: search merges registry hits
 * with local profiles, and a profile is created lazily the first time a registry entry is used (opened on the
 * client page or referenced by an imported movement file).
 */
@Service
class ClientProfileService(
    private val profileDao: ClientProfileDao,
    private val registry: ClientRegistryClient,
) {

    /** Registry hits first (merged with the local profile when one exists), then local-only profiles. */
    @Transactional(readOnly = true)
    fun search(query: String): List<ClientProfile> {
        val registryHits = registry.search(query)
        val local = profileDao.findAllByExternalRefIn(registryHits.map { it.externalRef }).associateBy { it.externalRef }
        val merged = registryHits.map { hit ->
            local[hit.externalRef] ?: ClientProfile(externalRef = hit.externalRef, name = hit.name, country = hit.country, segment = hit.segment)
        }
        val localOnly = profileDao.searchLocal(query).filter { it.externalRef !in local }
        return (merged + localOnly).distinctBy { it.externalRef }
    }

    @Transactional(readOnly = true)
    fun get(clientId: UUID): ClientProfile =
        profileDao.findById(clientId).orElseThrow { NotFoundException("Client", clientId) }

    /** Creates the local profile for a registry entry on first use. */
    @Transactional
    fun ensureProfile(externalRef: String): ClientProfile =
        profileDao.findByExternalRef(externalRef) ?: run {
            val entry = registry.findByRef(externalRef) ?: throw NotFoundException("Client", externalRef)
            profileDao.save(ClientProfile(externalRef = entry.externalRef, name = entry.name, country = entry.country, segment = entry.segment))
        }
}
