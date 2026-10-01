package com.bank.adv.hedges.api

import org.springframework.web.bind.annotation.*

/**
 * Hedge proposal endpoints used by the meeting screen.
 * @docs HEDGE-001
 */
@RestController
@RequestMapping("/api/v1/hedges")
class HedgeController(private val facade: HedgeFacade) {

    @GetMapping("/{clientId}/proposals")
    fun listProposals(@PathVariable clientId: String): List<HedgeProposalDto> =
        facade.listProposals(clientId)

    @PostMapping("/{clientId}/proposals")
    fun createProposal(@PathVariable clientId: String, @RequestBody req: CreateHedgeRequest): HedgeProposalDto =
        facade.create(clientId, req)

    @PostMapping("/{proposalId}/stress-test")
    fun stressTest(@PathVariable proposalId: String, @RequestBody scenario: StressScenarioDto): StressResultDto =
        facade.stressTest(proposalId, scenario)

    @DeleteMapping("/{proposalId}")
    fun delete(@PathVariable proposalId: String) = facade.delete(proposalId)
}
