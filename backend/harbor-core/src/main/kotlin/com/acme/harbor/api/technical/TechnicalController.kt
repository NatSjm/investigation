package com.acme.harbor.api.technical

import com.acme.harbor.HarborConstants
import org.springframework.beans.factory.annotation.Value
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

/**
 * Technical endpoints outside the OpenAPI contract (operators and the deployment pipeline, never the frontend):
 * the only hand-written request mappings of the application. `docs/_generated/api-index.md` lists them with
 * tag `(no contract)`.
 */
@RestController
@RequestMapping("/technical")   // relative to the servlet context path (HarborConstants.API_BASE_PATH)
class TechnicalController(@Value("\${harbor.version:dev}") private val version: String) {

    data class VersionInfo(val application: String, val version: String)

    @GetMapping("/version")
    fun version(): VersionInfo = VersionInfo(HarborConstants.APPLICATION_NAME, version)
}
