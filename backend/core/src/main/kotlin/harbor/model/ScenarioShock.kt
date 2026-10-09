package harbor.model

import harbor.utils.ScenarioPricePath
import java.math.BigDecimal

/** JSON shape of one entry of `market_scenario.shocks`; percentages are fractions (0.10 = +10 %). */
data class ScenarioShock(
    val fromMonth: Int,
    val priceChangePct: BigDecimal,
    val transportChangePct: BigDecimal,
) {
    fun toCalc() = ScenarioPricePath.Shock(fromMonth, priceChangePct, transportChangePct)
}
