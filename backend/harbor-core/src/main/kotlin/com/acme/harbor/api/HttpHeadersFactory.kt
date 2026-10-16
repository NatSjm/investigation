package com.acme.harbor.api

import org.springframework.http.ContentDisposition
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType

/** Response headers of the file downloads served by the controllers (PDF reports, exports). */
object HttpHeadersFactory {

    fun attachment(filename: String, mediaType: MediaType): HttpHeaders = HttpHeaders().apply {
        contentType = mediaType
        contentDisposition = ContentDisposition.attachment().filename(filename).build()
    }

    fun pdfAttachment(filename: String): HttpHeaders = attachment(filename, MediaType.APPLICATION_PDF)
}
