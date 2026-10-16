package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.ClientProfile
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.util.UUID

/** Local client profiles (table `client_profile`). */
@Repository
interface ClientProfileRepository : JpaRepository<ClientProfile, UUID> {

    fun findByExternalRef(externalRef: String): ClientProfile?

    fun findAllByExternalRefIn(externalRefs: Collection<String>): List<ClientProfile>

    @Query("select p from ClientProfile p where lower(p.name) like lower(concat('%', :q, '%')) or p.externalRef = :q")
    fun searchLocal(q: String): List<ClientProfile>
}
