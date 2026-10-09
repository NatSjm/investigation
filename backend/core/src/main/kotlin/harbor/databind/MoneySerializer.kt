package harbor.databind

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.SerializerProvider
import com.fasterxml.jackson.databind.ser.std.StdSerializer
import java.math.BigDecimal

/**
 * Writes amounts and ratios as plain JSON numbers that keep their scale (`1300.00`, `0.3000`) instead of the
 * default `1.3E+3` notation, so the frontend shows exactly what the calculations in `harbor.utils` rounded.
 */
class MoneySerializer : StdSerializer<BigDecimal>(BigDecimal::class.java) {

    override fun serialize(value: BigDecimal, gen: JsonGenerator, provider: SerializerProvider) {
        gen.writeNumber(value.toPlainString())
    }
}
