package com.acme.harbor.component

/**
 * Opens a binary spreadsheet (`.xls` / `.xlsx`) as a [WorkbookReader]. Registered as an optional bean named
 * `xlsWorkbookOpener` by the deployment that ships a spreadsheet library; absent in tests, where only
 * delimited fixtures are used.
 */
fun interface XlsWorkbookOpener {
    fun open(fileName: String, content: ByteArray): WorkbookReader
}
