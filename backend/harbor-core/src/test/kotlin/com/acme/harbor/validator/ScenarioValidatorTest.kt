package com.acme.harbor.validator

import com.acme.harbor.exception.ValidationException
import com.acme.harbor.model.ScenarioShock
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import java.math.BigDecimal

/** Rules of `ScenarioValidator` (market scenarios, MKT-001). Horizon of the examples: 24 months. */
class ScenarioValidatorTest {

    private val validator = ScenarioValidator()
    private val horizon = 24

    private fun shock(fromMonth: Int, price: String = "0.10", transport: String = "0.00") =
        ScenarioShock(fromMonth, BigDecimal(price), BigDecimal(transport))

    @Test
    fun `shocks inside the horizon are accepted`() {
        assertDoesNotThrow { validator.validate("Price spike", listOf(shock(1), shock(24, price = "-0.20")), horizon) }
    }

    @Test
    fun `blank name is rejected`() {
        val e = assertThrows<ValidationException> { validator.validate("  ", listOf(shock(1)), horizon) }
        assertEquals("Scenario name must not be blank", e.message)
    }

    @Test
    fun `shock after the end of the horizon is rejected`() {
        val e = assertThrows<ValidationException> { validator.validate("Late", listOf(shock(25)), horizon) }
        assertEquals("shock.fromMonth 25 outside horizon 1..24", e.message)
    }

    @Test
    fun `month index 0 is rejected`() {
        assertThrows<ValidationException> { validator.validate("Zero", listOf(shock(0)), horizon) }
    }

    @Test
    fun `a change of -100 percent or below is rejected`() {
        assertThrows<ValidationException> { validator.validate("Crash", listOf(shock(3, price = "-1.00")), horizon) }
        assertThrows<ValidationException> { validator.validate("Crash", listOf(shock(3, transport = "-1.50")), horizon) }
    }

    @Test
    fun `at most ten scenarios per session`() {
        assertDoesNotThrow { validator.validateCount(9) }
        assertThrows<ValidationException> { validator.validateCount(10) }
    }
}
