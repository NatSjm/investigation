package com.acme.harbor.component

import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.Resource
import org.springframework.core.io.ResourceLoader
import org.springframework.stereotype.Component

/**
 * Loads the meeting report template sent to document-service together with the payload reference:
 * `pdf/meeting-report.html` (property `harbor.reports.template`) with the stylesheet `pdf/report.css`
 * inlined in place of the `<link rel="stylesheet" href="report.css">` tag, so the renderer needs no second fetch.
 * The template is read once and cached; placeholders (`{{session.clientName}}`, ...) are filled by the renderer
 * from the JSON payload built by `ReportPayloadService`.
 */
@Component
class ReportTemplateLoader(
    private val resourceLoader: ResourceLoader,
    @Value("\${harbor.reports.template:classpath:pdf/meeting-report.html}") private val templateLocation: String,
) {

    private val template: String by lazy { inline(read(resourceLoader.getResource(templateLocation))) }

    /** HTML of the meeting report with the stylesheet inlined. */
    fun meetingReport(): String = template

    private fun inline(html: String): String {
        val css = read(resourceLoader.getResource(templateLocation.substringBeforeLast('/') + "/" + STYLESHEET))
        return html.replace(STYLESHEET_LINK, "<style>\n$css\n</style>")
    }

    private fun read(resource: Resource): String {
        check(resource.exists()) { "Report template resource $resource not found" }
        return resource.inputStream.use { it.readBytes().toString(Charsets.UTF_8) }
    }

    companion object {
        const val STYLESHEET = "report.css"
        const val STYLESHEET_LINK = """<link rel="stylesheet" href="report.css">"""
    }
}
