package harbor.event

import harbor.dao.GoodsMovementDao
import harbor.kafka.Topics
import harbor.kafka.events.MovementsLoadedEvent
import harbor.model.ImportBatch
import org.slf4j.LoggerFactory
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.stereotype.Component

/**
 * Produces `harbor.imports.movements-loaded` (key = batchId) after a batch has been stored, so that
 * Product1ProjectionRefreshListener / Product2ProjectionRefreshListener recompute the projections of open sessions.
 */
@Component
class MovementsLoadedPublisher(
    private val kafkaTemplate: KafkaTemplate<String, Any>,
    private val movementDao: GoodsMovementDao,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    fun publish(batch: ImportBatch) {
        val periodFrom = movementDao.minPeriodOfBatch(batch.id)
        val periodTo = movementDao.maxPeriodOfBatch(batch.id)
        if (periodFrom == null || periodTo == null) {
            log.info("Batch {} contains no accepted rows, nothing to publish", batch.id)
            return
        }
        val event = MovementsLoadedEvent(
            batchId = batch.id,
            clientIds = movementDao.clientIdsOfBatch(batch.id),
            periodFrom = periodFrom,
            periodTo = periodTo,
        )
        kafkaTemplate.send(Topics.MOVEMENTS_LOADED, batch.id.toString(), event)
        log.info("Published movements-loaded for batch {} ({} clients)", batch.id, event.clientIds.size)
    }
}
