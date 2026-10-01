package com.bank.adv.hedges.api

import org.springframework.stereotype.Service

/**
 * Module facade for hedge proposals. Read this file first; internals live in `calc/` and `messaging/`.
 *
 * Responsibilities: list/create proposals, run monthly cash-flow calculation, trigger stress tests,
 * publish `hedge.proposal.created`.
 */
@Service
class HedgeFacade(
    private val repo: HedgeProposalRepository,
    private val calculator: HedgeCashflowCalculator,
    private val publisher: HedgeEventPublisher,
) {
    fun listProposals(clientId: String): List<HedgeProposalDto> = repo.findByClient(clientId).map { it.toDto() }
    fun create(clientId: String, req: CreateHedgeRequest): HedgeProposalDto = TODO()
    fun stressTest(proposalId: String, scenario: StressScenarioDto): StressResultDto = TODO()
    fun delete(proposalId: String) = repo.delete(proposalId)
}
