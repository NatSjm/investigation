package com.acme.harbor.model

import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.utils.Rounding
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Key indicators of one product group on the client overview page, assembled by `ClientOverviewService`
 * (volume / value / sparkline from `movement_monthly`, role, cover ratio, number of open sessions).
 */
data class ClientOverviewIndicators(
    val productGroup: ProductGroup,
    val volume12m: BigDecimal = Rounding.ZERO_MONEY,
    val value12m: BigDecimal = Rounding.ZERO_MONEY,
    val role: ClientRole = ClientRole.UNDETERMINED,
    val coverRatio: BigDecimal = Rounding.ZERO_RATIO,
    val openSessions: Int = 0,
    /** Monthly value of the last 12 months, oldest first (sparkline chart). */
    val sparkline: List<Pair<YearMonth, BigDecimal>> = emptyList(),
)
