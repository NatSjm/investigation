package com.acme.harbor.validator

import com.acme.harbor.exception.ValidationException
import com.acme.harbor.model.ScenarioShock
import org.springframework.stereotype.Component
import java.math.BigDecimal

/**
 * Rules for market scenarios (`createScenario`, `updateScenario`):
 * - the name must not be blank,
 * - every shock starts inside the session horizon (`1 <= fromMonth <= horizonMonths`),
 * - a price or transport change must stay above -100 %,
 * - at most [MAX_SCENARIOS_PER_SESSION] scenarios per session.
 */
@Component
class ScenarioValidator {

    fun validate(name: String, shocks: List<ScenarioShock>, horizonMonths: Int) {
        ValidationException.check(name.isNotBlank()) { "Scenario name must not be blank" }
        shocks.forEach { shock ->
            ValidationException.check(shock.fromMonth in 1..horizonMonths) {
                "shock.fromMonth ${shock.fromMonth} outside horizon 1..$horizonMonths"
            }
            ValidationException.check(shock.priceChangePct > MIN_CHANGE && shock.transportChangePct > MIN_CHANGE) {
                "a change below -100 % is not allowed"
            }
        }
    }

    /** Called before a new scenario is created; [existing] is the number of scenarios of the session. */
    fun validateCount(existing: Int) {
        ValidationException.check(existing < MAX_SCENARIOS_PER_SESSION) { "At most $MAX_SCENARIOS_PER_SESSION scenarios per session" }
    }

    companion object {
        const val MAX_SCENARIOS_PER_SESSION = 10
        private val MIN_CHANGE = BigDecimal("-1")
    }
}
