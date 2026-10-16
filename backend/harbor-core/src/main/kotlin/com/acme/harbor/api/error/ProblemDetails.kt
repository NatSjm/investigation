package com.acme.harbor.api.error

import org.springframework.http.HttpStatus
import org.springframework.http.ProblemDetail
import java.net.URI

/**
 * The one place that shapes RFC 7807 `application/problem+json` bodies (schema `Problem` of the contract):
 * `title` = reason phrase, `detail` = the message (or the reason phrase), `instance` = the request path.
 * Used by `advice/GlobalExceptionAdvice` and by the filters that answer before MVC (`component/SessionHeaderFilter`).
 */
object ProblemDetails {

    fun of(status: HttpStatus, detail: String?, instance: String? = null): ProblemDetail =
        ProblemDetail.forStatusAndDetail(status, detail ?: status.reasonPhrase).apply {
            title = status.reasonPhrase
            if (instance != null) this.instance = URI.create(instance)
        }
}
