package harbor.event

import harbor.enums.ProductGroup
import harbor.kafka.Topics
import harbor.kafka.events.PricesUpdatedEvent
import harbor.service.BaselinePriceService
import harbor.utils.MonthGrid
import org.slf4j.LoggerFactory
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component
import java.time.Clock
import java.time.YearMonth

/**
 * Consumes `harbor.market.prices-updated` published by the external market-data service and refreshes the
 * local `baseline_price` rows for the maximum planning horizon of the affected product group.
 */
@Component
class MarketPricesListener(private val curves: BaselinePriceService, private val clock: Clock) {

    private val log = LoggerFactory.getLogger(javaClass)

    @KafkaListener(topics = [Topics.PRICES_UPDATED], groupId = "harbor-market")
    fun onPricesUpdated(event: PricesUpdatedEvent) {
        val productGroup = ProductGroup.fromWire(event.productGroup)
        if (event.corridor != productGroup.corridor) {
            log.warn("Ignoring prices-updated for unknown corridor {} of {}", event.corridor, productGroup)
            return
        }
        val from = YearMonth.now(clock)
        val to = from.plusMonths(MonthGrid.MAX_HORIZON.toLong())
        val rows = curves.refresh(productGroup, from, to)
        log.info("Baseline curve of {} refreshed from market-data (as of {}): {} months", productGroup, event.asOf, rows)
    }
}
