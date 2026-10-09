package harbor.kafka.events

import java.time.LocalDate
import java.util.UUID

/**
 * Payload of topic `Topics.MOVEMENTS_LOADED`. Key: batchId.
 * A daily import batch has been stored in `goods_movement`; the projections of the listed clients are stale.
 */
data class MovementsLoadedEvent(
    val batchId: UUID,
    val clientIds: List<UUID>,
    val periodFrom: LocalDate,
    val periodTo: LocalDate,
)
