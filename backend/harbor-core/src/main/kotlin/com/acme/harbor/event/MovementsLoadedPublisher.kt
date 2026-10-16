package com.acme.harbor.event

import com.acme.harbor.dao.repository.GoodsMovementRepository
import com.acme.harbor.kafka.events.MovementsLoaded
import com.acme.harbor.dao.model.ImportBatch
import org.slf4j.LoggerFactory
import com.acme.harbor.client.kafka.EventProducer
import org.springframework.stereotype.Component

/**
 * Produces `harbor.imports.movements-loaded` (key = batchId) after a batch has been stored, so that
 * Product1ProjectionRefreshListener / Product2ProjectionRefreshListener recompute the projections of open sessions.
 */
@Component
class MovementsLoadedPublisher(
    private val producer: EventProducer,
    private val movementRepository: GoodsMovementRepository,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    fun publish(batch: ImportBatch) {
        val periodFrom = movementRepository.minPeriodOfBatch(batch.id)
        val periodTo = movementRepository.maxPeriodOfBatch(batch.id)
        if (periodFrom == null || periodTo == null) {
            log.info("Batch {} contains no accepted rows, nothing to publish", batch.id)
            return
        }
        val event = MovementsLoaded(
            batch.id.toString(),
            movementRepository.clientIdsOfBatch(batch.id).map { it.toString() },
            periodFrom.toString(),
            periodTo.toString(),
        )
        producer.send(TOPIC, batch.id.toString(), event)
        log.info("Published movements-loaded for batch {} ({} clients)", batch.id, event.clientIds.size)
    }

    companion object {
        /** Consumed by Product1ProjectionRefreshListener and Product2ProjectionRefreshListener; schema `kafka-client/src/main/resources/avro/MovementsLoaded.avsc`. */
        const val TOPIC = "harbor.imports.movements-loaded"
    }
}
