package harbor.component

import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Qualifier
import org.springframework.stereotype.Component

/**
 * Opens the raw bytes delivered by file-exchange as a [WorkbookReader]: `.txt` / `.tsv` / `.csv` files are read
 * as delimited text ([WorkbookDelimitedReader]), everything else is handed to the optional [XlsWorkbookOpener].
 */
@Component
class WorkbookReaderFactory(
    @Autowired(required = false)
    @Qualifier("xlsWorkbookOpener")
    private val binaryOpener: XlsWorkbookOpener?,
) {

    fun open(fileName: String, content: ByteArray): WorkbookReader {
        val extension = fileName.substringAfterLast('.', "").lowercase()
        return when (extension) {
            "txt", "tsv" -> WorkbookDelimitedReader(content.toString(Charsets.UTF_8), '\t')
            "csv" -> WorkbookDelimitedReader(content.toString(Charsets.UTF_8), ';')
            else -> binaryOpener?.open(fileName, content)
                ?: throw IllegalStateException("No binary workbook reader configured for '$fileName'")
        }
    }
}
