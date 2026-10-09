package harbor.databind

import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.databind.DeserializationContext
import com.fasterxml.jackson.databind.deser.std.StdDeserializer
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.DateTimeParseException

/**
 * Reads a month (`period`) from `YYYY-MM` or from a full date `YYYY-MM-DD` (the first-of-month representation
 * used in the database columns and in some external payloads).
 */
class PeriodDeserializer : StdDeserializer<YearMonth>(YearMonth::class.java) {

    override fun deserialize(parser: JsonParser, context: DeserializationContext): YearMonth {
        val raw = parser.valueAsString?.trim().orEmpty()
        return try {
            if (raw.length > MONTH_LENGTH) YearMonth.from(LocalDate.parse(raw)) else YearMonth.parse(raw)
        } catch (e: DateTimeParseException) {
            context.handleWeirdStringValue(YearMonth::class.java, raw, "period must be YYYY-MM") as YearMonth
        }
    }

    companion object {
        private const val MONTH_LENGTH = 7
    }
}
