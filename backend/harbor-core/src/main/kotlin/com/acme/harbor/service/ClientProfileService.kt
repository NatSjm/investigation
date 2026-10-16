package com.acme.harbor.service

import com.acme.harbor.client.rest.ClientRegistryClient
import com.acme.harbor.dao.repository.ClientProfileRepository
import com.acme.harbor.exception.NotFoundException
import com.acme.harbor.dao.model.ClientProfile
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
    private val profileRepository: ClientProfileRepository,
    private val registry: ClientRegistryClient,
) {

    /** Registry hits first (merged with the local profile when one exists), then local-only profiles. */
    @Transactional
    fun search(query: String): List<ClientProfile> {
        val registryHits = registry.search(query)
        val local = profileRepository.findAllByExternalRefIn(registryHits.map { it.externalRef }).associateBy { it.externalRef }
        val merged = registryHits.map { hit ->
            local[hit.externalRef] ?: profileRepository.save(ClientProfile(externalRef = hit.externalRef, name = hit.name, country = hit.country, segment = hit.segment))   // registry hits get a stable local id on first sight
        }
        val localOnly = profileRepository.searchLocal(query).filter { it.externalRef !in local }
        return (merged + localOnly).distinctBy { it.externalRef }
    }

    @Transactional(readOnly = true)
    fun get(clientId: UUID): ClientProfile =
        profileRepository.findById(clientId).orElseThrow { NotFoundException("Client", clientId) }

    /** Creates the local profile for a registry entry on first use. */
    @Transactional
    fun ensureProfile(externalRef: String): ClientProfile =
        profileRepository.findByExternalRef(externalRef) ?: run {
            val entry = registry.findByRef(externalRef) ?: throw NotFoundException("Client", externalRef)
            profileRepository.save(ClientProfile(externalRef = entry.externalRef, name = entry.name, country = entry.country, segment = entry.segment))
        }
}
