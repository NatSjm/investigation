package com.acme.harbor.manager

import com.acme.harbor.dao.model.ImportBatch
import com.acme.harbor.service.MovementImportService
import org.springframework.stereotype.Service
import java.time.YearMonth

/**
 * Daily XLS movement import and monthly snapshot (entry point of `DailyMovementImportJob` and `MonthlySnapshotJob`).
 *
 * The import pulls every file received by file-exchange since the last batch, parses it with `XlsMovementParser`
 * into `goods_movement` (one `import_batch` per file, rejected rows counted, never blocking the batch) and
 * publishes `harbor.imports.movements-loaded`. The snapshot rolls one month up into `movement_monthly`, the
 * input of the role classification and the projections.
 *
 * @docs IMP-001
 */
@Service
class ImportManager(
    private val importService: MovementImportService,
) {

    /** Imports all new files; [scheduled] distinguishes the nightly run from the admin trigger in the log. */
    fun importNewFiles(scheduled: Boolean): List<ImportBatch> =
        importService.importNewFiles(if (scheduled) MovementImportService.Trigger.SCHEDULED else MovementImportService.Trigger.MANUAL)

    fun snapshotMonth(month: YearMonth): Int = importService.snapshotMonth(month)

    fun recentBatches(): List<ImportBatch> = importService.recentBatches()
}
