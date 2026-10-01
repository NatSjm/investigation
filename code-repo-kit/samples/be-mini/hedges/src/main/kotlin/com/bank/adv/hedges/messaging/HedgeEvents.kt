package com.bank.adv.hedges.messaging

import org.springframework.kafka.annotation.KafkaListener
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.stereotype.Component

object Topics {
    const val PROPOSAL_CREATED = "hedge.proposal.created"
    const val MARKET_RATES = "market.rates.updated"
}

@Component
class HedgeEventPublisher(private val kafka: KafkaTemplate<String, Any>) {
    fun proposalCreated(evt: HedgeProposalCreated) = kafka.send(Topics.PROPOSAL_CREATED, evt.proposalId, evt)
}

@Component
class MarketRatesListener(private val rates: RateCache) {
    @KafkaListener(topics = [Topics.MARKET_RATES], groupId = "hedges")
    fun onRates(evt: MarketRatesUpdated) = rates.update(evt)

    @KafkaListener(topics = ["client.kyc.changed"], groupId = "hedges")
    fun onKyc(evt: Map<String, Any>) = Unit
}
