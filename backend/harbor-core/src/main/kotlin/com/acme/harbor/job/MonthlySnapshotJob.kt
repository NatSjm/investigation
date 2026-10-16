package com.acme.harbor.job

import com.acme.harbor.manager.ImportManager
import org.slf4j.LoggerFactory
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component
import java.time.Clock
import java.time.YearMonth

/**
 * Rolls the previous calendar month of `goods_movement` up into `movement_monthly`.
 * Runs on the 1st of every month at 03:00, after the daily import of that night.
 */
@Component
class MonthlySnapshotJob(private val importManager: ImportManager, private val clock: Clock) {

    private val log = LoggerFactory.getLogger(javaClass)

    /** Rebuilds movement_monthly for the previous calendar month. */
    @Scheduled(cron = "0 0 3 1 * *")
    fun run() {
        val month = YearMonth.now(clock).minusMonths(1)
        val rows = importManager.snapshotMonth(month)
        log.info("Monthly snapshot for {} written: {} rows", month, rows)
    }
}
