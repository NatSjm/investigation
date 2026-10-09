package harbor.service

import harbor.dao.MeetingSessionDao
import harbor.dao.MovementMonthlyDao
import harbor.enums.ProductGroup
import harbor.enums.SessionStatus
import harbor.model.ClientOverviewIndicators
import harbor.utils.MonthGrid
import harbor.utils.Rounding
import harbor.utils.sumMoney
import harbor.utils.toPeriodDate
import harbor.utils.toYearMonth
import org.springframework.stereotype.Service
import java.time.Clock
import java.time.LocalDate
import java.util.UUID

/**
 * Key indicators per product group for the client overview page: last-12-month volume, value and sparkline
 * from `movement_monthly`, current role ([ClientRoleService]), cover ratio ([CoverRatioService]) and the
 * number of OPEN meeting sessions.
 */
@Service
class ClientOverviewService(
    private val monthlyDao: MovementMonthlyDao,
    private val sessionDao: MeetingSessionDao,
    private val roleService: ClientRoleService,
    private val coverRatioService: CoverRatioService,
    private val clock: Clock,
) {

    fun indicators(clientId: UUID): List<ClientOverviewIndicators> = ProductGroup.entries.map { indicators(clientId, it) }

    fun indicators(clientId: UUID, productGroup: ProductGroup): ClientOverviewIndicators {
        val months = MonthGrid.lastFullMonths(LocalDate.now(clock))
        val rows = monthlyDao.findAllByClientIdAndProductGroupAndPeriodBetween(
            clientId, productGroup, months.first().toPeriodDate(), months.last().toPeriodDate(),
        )
        val valueByMonth = rows.groupBy { it.period.toYearMonth() }.mapValues { (_, r) -> r.map { it.value }.sumMoney() }
        return ClientOverviewIndicators(
            productGroup = productGroup,
            volume12m = rows.map { it.quantity }.sumMoney(),
            value12m = rows.map { it.value }.sumMoney(),
            role = roleService.currentRole(clientId, productGroup),
            coverRatio = coverRatioService.lastTwelveMonthsRatio(clientId, productGroup),
            openSessions = sessionDao.countByClientIdAndProductGroupAndStatus(clientId, productGroup, SessionStatus.OPEN),
            sparkline = months.map { it to (valueByMonth[it] ?: Rounding.ZERO_MONEY) },
        )
    }
}
