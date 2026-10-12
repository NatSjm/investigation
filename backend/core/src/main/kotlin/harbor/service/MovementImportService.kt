package harbor.service

import harbor.client.FileExchangeClient
import harbor.component.WorkbookReaderFactory
import harbor.component.XlsMovementParser
import harbor.dao.GoodsMovementDao
import harbor.dao.ImportBatchDao
import harbor.dao.MovementMonthlyDao
import harbor.event.MovementsLoadedPublisher
import harbor.model.GoodsMovement
import harbor.model.ImportBatch
import harbor.utils.toPeriodDate
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.transaction.support.TransactionTemplate
import java.time.Clock
import java.time.Duration
import java.time.Instant
import java.time.YearMonth
import java.util.UUID

/**
 * Daily XLS movement import and monthly snapshot.
 *
 * [importNewFiles] pulls every file received by file-exchange since the last batch, parses it with
 * [XlsMovementParser] into `goods_movement` (one `import_batch` per file, rejected rows counted, never
 * blocking the batch), rolls the imported months up into `movement_monthly` and publishes `harbor.imports.movements-loaded`. [snapshotMonth] rolls one month up
 * into `movement_monthly`, the input of the role classification and the projections.
 */
@Service
class MovementImportService(
    private val batchDao: ImportBatchDao,
    private val movementDao: GoodsMovementDao,
    private val monthlyDao: MovementMonthlyDao,
    private val fileExchange: FileExchangeClient,
    private val readerFactory: WorkbookReaderFactory,
    private val parser: XlsMovementParser,
    private val publisher: MovementsLoadedPublisher,
    private val transactionTemplate: TransactionTemplate,
    private val clientProfiles: ClientProfileService,
    private val clock: Clock,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    enum class Trigger { SCHEDULED, MANUAL }

    fun importNewFiles(trigger: Trigger): List<ImportBatch> {
        val since = batchDao.findFirstByOrderByReceivedAtDesc()?.receivedAt
            ?: Instant.now(clock).minus(Duration.ofDays(DEFAULT_LOOKBACK_DAYS))
        val files = fileExchange.listSince(since).filterNot { batchDao.existsBySourceFile(it.name) }
        log.info("{} import: {} new file(s) since {}", trigger, files.size, since)
        return files.map { importFile(it) }
    }

    /** Imports one file in its own transaction so that a broken file does not roll back the others. */
    @Transactional
    fun importFile(file: FileExchangeClient.ExchangeFileRef): ImportBatch {
        val batch = batchDao.save(ImportBatch(sourceFile = file.name, receivedAt = file.receivedAt))
        try {
            val result = readerFactory.open(file.name, fileExchange.content(file.id)).use { parser.parse(it) }
            val clientIds = mutableMapOf<String, UUID>()
            val rows = result.accepted.map { parsed ->
                val clientId = clientIds.getOrPut(parsed.clientRef) { clientProfiles.ensureProfile(parsed.clientRef).id }
                GoodsMovement(
                    clientId = clientId,
                    batchId = batch.id,
                    productGroup = parsed.productGroup,
                    subProduct = parsed.subProduct,
                    city = parsed.city,
                    transportMode = parsed.transportMode,
                    direction = parsed.direction,
                    period = parsed.period.toPeriodDate(),
                    quantity = parsed.quantity,
                    unitPrice = parsed.unitPrice,
                    priceBasis = parsed.priceBasis,
                )
            }
            movementDao.saveAll(rows)
            // roll the touched months up at once so indicators and role classification see the new actuals today;
            // the monthly snapshot job re-rolls the closed month on the 1st (idempotent: delete + re-aggregate per period)
            transactionTemplate.executeWithoutResult { rows.map { it.period }.distinct().forEach { period -> monthlyDao.deleteAllByPeriod(period); movementDao.rollUpMonth(period) } }
            batch.finish(total = result.total, rejected = result.rejected.size)
            result.rejected.take(MAX_LOGGED_REJECTS).forEach { log.warn("Batch {} row {}/{} rejected: {}", batch.id, it.sheet, it.rowNumber, it.reason) }
            publisher.publish(batch)
        } catch (e: Exception) {
            log.error("Import of {} failed", file.name, e)
            batch.fail()
        }
        return batchDao.save(batch)
    }

    @Transactional
    fun snapshotMonth(month: YearMonth): Int {
        val period = month.toPeriodDate()
        monthlyDao.deleteAllByPeriod(period)
        return movementDao.rollUpMonth(period)
    }

    fun recentBatches(): List<ImportBatch> = batchDao.findTop50ByOrderByReceivedAtDesc()

    companion object {
        const val DEFAULT_LOOKBACK_DAYS = 7L
        const val MAX_LOGGED_REJECTS = 20
    }
}
