package harbor.service

import harbor.dao.ClientRoleDao
import harbor.dao.MovementMonthlyDao
import harbor.enums.ClientRole
import harbor.enums.ParameterKey
import harbor.enums.ProductGroup
import harbor.enums.RoleSource
import harbor.model.ClientRoleDecision
import harbor.utils.MonthGrid
import harbor.utils.RoleClassifier
import harbor.utils.toPeriodDate
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.Clock
import java.time.Instant
import java.time.LocalDate
import java.util.UUID

/**
 * Applies calculation `client_role_classification` ([RoleClassifier]) to the last 12 full months of actual
 * movements (`movement_monthly`) and keeps the decision history in `client_role`.
 *
 * Thresholds (`role.min_volume`, `role.importer_threshold`, `role.exporter_threshold`) come from
 * [ParameterService] (`parameter_set`).
 */
@Service
class ClientRoleService(
    private val roleDao: ClientRoleDao,
    private val monthlyDao: MovementMonthlyDao,
    private val parameters: ParameterService,
    private val clock: Clock,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    data class Classification(val result: RoleClassifier.Result, val decision: ClientRoleDecision)

    fun thresholds(): RoleClassifier.Thresholds = RoleClassifier.Thresholds(
        minVolume = parameters.required(ParameterKey.ROLE_MIN_VOLUME),
        importerThreshold = parameters.required(ParameterKey.ROLE_IMPORTER_THRESHOLD),
        exporterThreshold = parameters.required(ParameterKey.ROLE_EXPORTER_THRESHOLD),
    )

    /** Runs the algorithm without persisting anything. */
    fun classify(clientId: UUID, productGroup: ProductGroup): RoleClassifier.Result {
        val months = MonthGrid.lastFullMonths(LocalDate.now(clock))
        val movements = monthlyDao
            .findAllByClientIdAndProductGroupAndPeriodBetween(clientId, productGroup, months.first().toPeriodDate(), months.last().toPeriodDate())
            .map { RoleClassifier.Movement(it.direction, it.quantity) }
        return RoleClassifier.classify(movements, thresholds())
    }

    /** Runs the algorithm and records the result unless the newest decision is an identical ALGORITHM row. */
    @Transactional
    fun classifyAndRecord(clientId: UUID, productGroup: ProductGroup): Classification {
        val result = classify(clientId, productGroup)
        val latest = roleDao.findFirstByClientIdAndProductGroupOrderByDecidedAtDesc(clientId, productGroup)
        val decision = if (latest != null && latest.source == RoleSource.ALGORITHM && latest.role == result.role) {
            latest
        } else {
            roleDao.save(
                ClientRoleDecision(
                    clientId = clientId,
                    productGroup = productGroup,
                    role = result.role,
                    source = RoleSource.ALGORITHM,
                    reason = result.share?.let { "inbound share $it" } ?: "total volume below role.min_volume",
                    decidedAt = Instant.now(clock),
                ),
            )
        }
        return Classification(result, decision)
    }

    /** Current role: the newest decision (manual overrides win because they are newer), else a fresh classification. */
    fun currentRole(clientId: UUID, productGroup: ProductGroup): ClientRole =
        roleDao.findFirstByClientIdAndProductGroupOrderByDecidedAtDesc(clientId, productGroup)?.role
            ?: classifyAndRecord(clientId, productGroup).result.role

    /** Role shown in a session: the manual override of the session, else the client's current role. */
    fun sessionRole(clientId: UUID, productGroup: ProductGroup, roleOverride: ClientRole?): ClientRole =
        roleOverride ?: currentRole(clientId, productGroup)

    fun history(clientId: UUID, productGroup: ProductGroup): List<ClientRoleDecision> =
        roleDao.findAllByClientIdAndProductGroupOrderByDecidedAtDesc(clientId, productGroup)

    /** Records a manual override decided during a meeting (see `ClientRoleSessionClosedListener`). */
    @Transactional
    fun recordOverride(clientId: UUID, productGroup: ProductGroup, role: ClientRole, reason: String?): ClientRoleDecision {
        log.info("Recording manual role override {} for client {} / {}", role, clientId, productGroup)
        return roleDao.save(
            ClientRoleDecision(
                clientId = clientId,
                productGroup = productGroup,
                role = role,
                source = RoleSource.MANUAL,
                reason = reason,
                decidedAt = Instant.now(clock),
            ),
        )
    }
}
