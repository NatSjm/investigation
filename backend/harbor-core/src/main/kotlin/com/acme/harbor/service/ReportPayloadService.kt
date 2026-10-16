package com.acme.harbor.service

import com.acme.harbor.dao.repository.MarketScenarioRepository
import com.acme.harbor.dao.service.MeetingSessionDaoService
import com.acme.harbor.dao.repository.ProjectionRepository
import com.acme.harbor.dao.repository.SessionClientConfigRepository
import com.acme.harbor.dao.repository.StressTestResultRepository
import com.acme.harbor.exception.NotFoundException
import com.acme.harbor.utils.ProjectionAggregator.Line
import com.acme.harbor.utils.ProjectionAggregator.Tables
import org.springframework.stereotype.Service
import java.time.Clock
import java.time.Instant
import java.util.UUID

/**
 * Builds the report payload stored in `meeting_report.payload` and rendered by document-service with the
 * `pdf/meeting-report.html` template: session header, the four projection tables, the scenarios of the
 * session and the `stress_test_result` rows per scenario (the stress chart is drawn by the renderer from
 * those rows). Works from the stored tables only, so it runs after the session is closed (no `SessionContext`).
 */
@Service
class ReportPayloadService(
    private val sessions: MeetingSessionDaoService,
    private val configRepository: SessionClientConfigRepository,
    private val clientProfiles: ClientProfileService,
    private val projectionRepository: ProjectionRepository,
    private val scenarioRepository: MarketScenarioRepository,
    private val stressRepository: StressTestResultRepository,
    private val clock: Clock,
) {

    fun build(sessionId: UUID): Map<String, Any?> {
        val session = sessions.require(sessionId)
        val config = configRepository.findById(sessionId).orElseThrow { NotFoundException("Session configuration", sessionId) }
        val tables = projectionRepository.load(sessionId)
        val scenarios = scenarioRepository.findAllBySessionIdOrderByCreatedAt(sessionId)
        val stressRows = stressRepository.findAllBySessionIdOrderByScenarioIdAscDimensionValueAscPeriodAsc(sessionId).groupBy { it.scenarioId }

        return mapOf(
            "schemaVersion" to SCHEMA_VERSION,
            "generatedAt" to Instant.now(clock).toString(),
            "session" to mapOf(
                "sessionId" to session.id.toString(),
                "kind" to session.kind.name,
                "productGroup" to session.productGroup.wireValue,
                "clientId" to session.clientId.toString(),
                "clientName" to clientProfiles.get(session.clientId).name,
                "representativeId" to session.representativeId,
                "startedAt" to session.startedAt.toString(),
                "closedAt" to session.closedAt?.toString(),
                "horizonMonths" to config.horizonMonths,
                "priceBasis" to config.priceBasis.name,
                "roleOverride" to session.roleOverride?.name,
                "roleOverrideReason" to session.roleOverrideReason,
                "parameterSnapshot" to session.parameterSnapshot,
            ),
            "projectionSummary" to summary(tables),
            "projectionTables" to tables(tables),
            "scenarios" to scenarios.map { s ->
                mapOf(
                    "scenarioId" to s.id.toString(),
                    "name" to s.name,
                    "kind" to s.kind.name,
                    "shocks" to s.shocks.map { mapOf("fromMonth" to it.fromMonth, "priceChangePct" to it.priceChangePct, "transportChangePct" to it.transportChangePct) },
                    "stressTest" to stressRows[s.id].orEmpty().map { r ->
                        mapOf(
                            "period" to r.period.toString(),
                            "dimensionValue" to r.dimensionValue,
                            "exposure" to r.exposure,
                            "transportCostDelta" to r.transportCostDelta,
                            "cumulativeExposure" to r.cumulativeExposure,
                        )
                    },
                )
            },
        )
    }

    private fun summary(tables: Tables?): List<Map<String, Any?>> = tables?.summary.orEmpty().map { s ->
        mapOf(
            "period" to s.period.toString(),
            "totalQuantity" to s.totalQuantity,
            "totalValue" to s.totalValue,
            "totalLandedCost" to s.totalLandedCost,
            "coverRatio" to s.coverRatio,
            "cumulativeValue" to s.cumulativeValue,
        )
    }

    /** By sub-product, by dimension and by direction (the summary table is [summary]). */
    private fun tables(tables: Tables?): Map<String, Any?> {
        if (tables == null) return emptyMap()
        fun lines(list: List<Line>) = list.map {
            mapOf("period" to it.period.toString(), "key" to it.key, "quantity" to it.quantity, "value" to it.value,
                "landedCost" to it.landedCost, "cumulativeValue" to it.cumulativeValue)
        }
        return mapOf(
            "dimensionKind" to tables.dimensionKind.name,
            "bySubProduct" to lines(tables.bySubProduct),
            "byDimension" to lines(tables.byDimension),
            "byDirection" to lines(tables.byDirection),
        )
    }

    companion object {
        const val SCHEMA_VERSION = 2
    }
}
