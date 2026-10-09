package harbor.component

/**
 * Minimal abstraction over a spreadsheet so that [XlsMovementParser] can be unit-tested with plain lists
 * and the application does not depend on a spreadsheet library. Every row is a list of cell strings
 * (empty string for blank cells), the first row of a sheet is the header. Instances are opened by
 * [WorkbookReaderFactory].
 */
interface WorkbookReader : AutoCloseable {

    /** Sheet names in workbook order. */
    fun sheets(): List<String>

    /** Rows of [sheet], header included, as trimmed cell strings. */
    fun rows(sheet: String): Sequence<List<String>>

    override fun close() {}
}
