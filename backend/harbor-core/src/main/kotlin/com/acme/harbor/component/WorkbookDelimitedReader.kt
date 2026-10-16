package com.acme.harbor.component

/**
 * Reader for the tab- or semicolon-separated export some senders still deliver instead of a real XLS file
 * (one sheet named "movements"). Binary workbooks go through [XlsWorkbookOpener].
 */
class WorkbookDelimitedReader(private val text: String, private val delimiter: Char = '\t') : WorkbookReader {

    override fun sheets(): List<String> = listOf(DEFAULT_SHEET)

    override fun rows(sheet: String): Sequence<List<String>> =
        text.lineSequence()
            .filter { it.isNotBlank() }
            .map { line -> line.split(delimiter).map { it.trim() } }

    companion object {
        const val DEFAULT_SHEET = "movements"
    }
}
