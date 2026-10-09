package harbor.component

import harbor.enums.Direction
import harbor.enums.PriceBasis
import harbor.enums.ProductGroup
import harbor.enums.TransportMode
import org.springframework.stereotype.Component
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Parses the daily movement workbook delivered by file-exchange.
 *
 * Expected columns (header names, any order, case-insensitive):
 *
 * | column           | content                                            |
 * |------------------|----------------------------------------------------|
 * | `client_ref`     | external reference of the client (client-registry) |
 * | `product_group`  | `product1` / `product2`                            |
 * | `sub_product`    | e.g. `P1-STD`, `P2-M`                              |
 * | `city`           | city hub (`Aldmoor`, ...), may be empty             |
 * | `transport_mode` | `ROAD` / `RAIL` / `SEA` / `AIR`, may be empty      |
 * | `direction`      | `IN` / `OUT`                                       |
 * | `period`         | `YYYY-MM`                                          |
 * | `quantity`       | decimal, > 0                                       |
 * | `unit_price`     | decimal, >= 0                                      |
 * | `price_basis`    | `VLD` / `NRL` / `CST` / `MRD`                      |
 *
 * Rows that cannot be parsed are reported as [RejectedRow] with the sheet, 1-based row number and reason;
 * the batch continues. The price basis must belong to the corridor of the product group.
 */
@Component
class XlsMovementParser {

    data class ParsedMovement(
        val clientRef: String,
        val productGroup: ProductGroup,
        val subProduct: String,
        val city: String?,
        val transportMode: TransportMode?,
        val direction: Direction,
        val period: YearMonth,
        val quantity: BigDecimal,
        val unitPrice: BigDecimal,
        val priceBasis: PriceBasis,
    )

    data class RejectedRow(val sheet: String, val rowNumber: Int, val reason: String)

    data class ParseResult(val accepted: List<ParsedMovement>, val rejected: List<RejectedRow>) {
        val total: Int get() = accepted.size + rejected.size
    }

    fun parse(reader: WorkbookReader): ParseResult {
        val accepted = mutableListOf<ParsedMovement>()
        val rejected = mutableListOf<RejectedRow>()
        for (sheet in reader.sheets()) {
            val iterator = reader.rows(sheet).iterator()
            if (!iterator.hasNext()) continue
            val header = indexHeader(iterator.next())
            val missing = REQUIRED_COLUMNS - header.keys
            if (missing.isNotEmpty()) {
                rejected += RejectedRow(sheet, 1, "missing columns: ${missing.joinToString()}")
                continue
            }
            var rowNumber = 1
            while (iterator.hasNext()) {
                val cells = iterator.next()
                rowNumber++
                if (cells.all { it.isBlank() }) continue
                runCatching { parseRow(cells, header) }
                    .onSuccess { accepted += it }
                    .onFailure { rejected += RejectedRow(sheet, rowNumber, it.message ?: it.javaClass.simpleName) }
            }
        }
        return ParseResult(accepted, rejected)
    }

    private fun indexHeader(headerRow: List<String>): Map<String, Int> =
        headerRow.mapIndexed { index, name -> name.trim().lowercase() to index }
            .filter { it.first.isNotEmpty() }
            .toMap()

    private fun parseRow(cells: List<String>, header: Map<String, Int>): ParsedMovement {
        fun cell(column: String): String = header[column]?.let { cells.getOrNull(it) }?.trim().orEmpty()
        fun required(column: String): String = cell(column).ifEmpty { throw IllegalArgumentException("$column is empty") }

        val productGroup = ProductGroup.fromWire(required(COL_PRODUCT_GROUP))
        val priceBasis = enumOrFail<PriceBasis>(required(COL_PRICE_BASIS), COL_PRICE_BASIS)
        require(priceBasis in productGroup.priceBases) { "price_basis $priceBasis does not belong to ${productGroup.wireValue}" }
        val quantity = decimal(required(COL_QUANTITY), COL_QUANTITY)
        require(quantity.signum() > 0) { "quantity must be positive" }
        val unitPrice = decimal(required(COL_UNIT_PRICE), COL_UNIT_PRICE)
        require(unitPrice.signum() >= 0) { "unit_price must not be negative" }

        return ParsedMovement(
            clientRef = required(COL_CLIENT_REF),
            productGroup = productGroup,
            subProduct = required(COL_SUB_PRODUCT).uppercase(),
            city = cell(COL_CITY).ifEmpty { null },
            transportMode = cell(COL_TRANSPORT_MODE).ifEmpty { null }?.let { enumOrFail<TransportMode>(it, COL_TRANSPORT_MODE) },
            direction = enumOrFail<Direction>(required(COL_DIRECTION), COL_DIRECTION),
            period = runCatching { YearMonth.parse(required(COL_PERIOD)) }
                .getOrElse { throw IllegalArgumentException("period must be YYYY-MM") },
            quantity = quantity,
            unitPrice = unitPrice,
            priceBasis = priceBasis,
        )
    }

    private fun decimal(raw: String, column: String): BigDecimal =
        runCatching { BigDecimal(raw.replace(',', '.').replace(" ", "")) }
            .getOrElse { throw IllegalArgumentException("$column is not a number: '$raw'") }

    private inline fun <reified E : Enum<E>> enumOrFail(raw: String, column: String): E =
        enumValues<E>().firstOrNull { it.name.equals(raw.trim(), ignoreCase = true) }
            ?: throw IllegalArgumentException("$column has unknown value '$raw'")

    companion object {
        const val COL_CLIENT_REF = "client_ref"
        const val COL_PRODUCT_GROUP = "product_group"
        const val COL_SUB_PRODUCT = "sub_product"
        const val COL_CITY = "city"
        const val COL_TRANSPORT_MODE = "transport_mode"
        const val COL_DIRECTION = "direction"
        const val COL_PERIOD = "period"
        const val COL_QUANTITY = "quantity"
        const val COL_UNIT_PRICE = "unit_price"
        const val COL_PRICE_BASIS = "price_basis"

        val REQUIRED_COLUMNS = setOf(
            COL_CLIENT_REF, COL_PRODUCT_GROUP, COL_SUB_PRODUCT, COL_DIRECTION,
            COL_PERIOD, COL_QUANTITY, COL_UNIT_PRICE, COL_PRICE_BASIS,
        )
    }
}
