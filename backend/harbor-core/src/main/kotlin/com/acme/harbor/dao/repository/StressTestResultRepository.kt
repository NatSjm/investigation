package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.StressTestResult
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.stereotype.Repository
import java.util.UUID

/** Stored stress test rows per session, scenario, dimension value and month (table `stress_test_result`). */
@Repository
interface StressTestResultRepository : JpaRepository<StressTestResult, Long> {

    fun findAllBySessionIdOrderByScenarioIdAscDimensionValueAscPeriodAsc(sessionId: UUID): List<StressTestResult>

    @Modifying
    fun deleteAllBySessionId(sessionId: UUID): Int
}
