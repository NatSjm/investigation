package harbor.kafka.events

import java.time.Instant

/**
 * Payload of topic `Topics.PRICES_UPDATED`, published by the external market-data service. Key: productGroup.
 *
 * @property productGroup wire value of the product group (`product1` / `product2`)
 * @property corridor corridor code (`VLD-NRL` / `CST-MRD`)
 */
data class PricesUpdatedEvent(
    val productGroup: String,
    val corridor: String,
    val asOf: Instant,
)
