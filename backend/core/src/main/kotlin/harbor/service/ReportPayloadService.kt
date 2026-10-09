package harbor.service

import harbor.dao.MarketScenarioDao
import harbor.dao.MeetingSessionDao
import harbor.dao.ProjectionDao
import harbor.dao.SessionClientConfigDao
import harbor.dao.StressTestResultDao
import harbor.exception.NotFoundException
import harbor.utils.ProjectionAggregator.Line
import harbor.utils.ProjectionAggregator.Tables
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
    private val sessionDao: MeetingSessionDao,
    private val configDao: SessionClientConfigDao,
    private val clientProfiles: ClientProfileService,
    private val projectionDao: ProjectionDao,
    private val scenarioDao: MarketScenarioDao,
    private val stressDao: StressTestResultDao,
    private val clock: Clock,
) {

    fun build(sessionId: UUID): Map<String, Any?> {
        val session = sessionDao.findById(sessionId).orElseThrow { NotFoundException("Session", sessionId) }
        val config = configDao.findById(sessionId).orElseThrow { NotFoundException("Session configuration", sessionId) }
        val tables = projectionDao.load(sessionId)
        val scenarios = scenarioDao.findAllBySessionIdOrderByCreatedAt(sessionId)
        val stressRows = stressDao.findAllBySessionIdOrderByScenarioIdAscDimensionValueAscPeriodAsc(sessionId).groupBy { it.scenarioId }

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
