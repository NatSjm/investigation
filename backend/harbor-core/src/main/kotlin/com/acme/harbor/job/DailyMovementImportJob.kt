package com.acme.harbor.job

import com.acme.harbor.manager.ImportManager
import net.javacrumbs.shedlock.spring.annotation.SchedulerLock
import org.slf4j.LoggerFactory
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component

/**
 * Daily import of the XLS movement files delivered by file-exchange. Runs at 02:00 server time; the same
 * work can be started by hand through `POST /admin/imports/run` (`AdminManager.triggerImport`).
 */
@Component
class DailyMovementImportJob(private val importManager: ImportManager) {

    private val log = LoggerFactory.getLogger(javaClass)

    /** Imports every new file from file-exchange into goods_movement and publishes movements-loaded. */
    @Scheduled(cron = "0 0 2 * * *")
    @SchedulerLock(name = "dailyMovementImport", lockAtLeastFor = "PT1M", lockAtMostFor = "PT2H")
    fun run() {
        log.info("Daily movement import started")
        val batches = importManager.importNewFiles(scheduled = true)
        log.info("Daily movement import finished: {} batch(es)", batches.size)
    }
}
