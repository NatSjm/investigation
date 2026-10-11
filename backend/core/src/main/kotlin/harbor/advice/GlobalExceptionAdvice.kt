package harbor.advice

import harbor.exception.MissingParameterException
import harbor.exception.NotFoundException
import harbor.exception.SessionClosedException
import harbor.exception.SessionHeaderMissingException
import harbor.exception.SessionNotBoundException
import harbor.exception.ValidationException
import jakarta.servlet.http.HttpServletRequest
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.http.ProblemDetail
import org.springframework.http.converter.HttpMessageNotReadableException
import org.springframework.web.bind.MethodArgumentNotValidException
import org.springframework.web.HttpRequestMethodNotSupportedException
import org.springframework.web.bind.MissingServletRequestParameterException
import org.springframework.web.servlet.resource.NoResourceFoundException
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice
import java.net.URI

/**
 * Maps exceptions to RFC 7807 `application/problem+json` bodies (the `Problem` schema of the contract):
 * - [NotFoundException], `NoSuchElementException`               -> 404
 * - [ValidationException], `IllegalArgumentException`, bean validation -> 400
 * - missing / malformed request parameter or body                 -> 400
 * - [SessionHeaderMissingException]                             -> 428
 * - [SessionClosedException], other `IllegalStateException`      -> 409
 * - [SessionNotBoundException], [MissingParameterException]       -> 500 (programming or configuration error)
 */
@RestControllerAdvice
class GlobalExceptionAdvice {

    private val log = LoggerFactory.getLogger(javaClass)

    @ExceptionHandler(NotFoundException::class, NoSuchElementException::class)
    fun notFound(e: RuntimeException, request: HttpServletRequest): ProblemDetail =
        problem(HttpStatus.NOT_FOUND, e.message, request)

    @ExceptionHandler(ValidationException::class, IllegalArgumentException::class)
    fun badRequest(e: RuntimeException, request: HttpServletRequest): ProblemDetail =
        problem(HttpStatus.BAD_REQUEST, e.message, request)

    @ExceptionHandler(HttpRequestMethodNotSupportedException::class)
    fun methodNotAllowed(e: HttpRequestMethodNotSupportedException, request: HttpServletRequest): ProblemDetail =
        problem(HttpStatus.METHOD_NOT_ALLOWED, e.message, request)

    @ExceptionHandler(NoResourceFoundException::class)
    fun noResource(e: NoResourceFoundException, request: HttpServletRequest): ProblemDetail =
        problem(HttpStatus.NOT_FOUND, "No such resource", request)

    @ExceptionHandler(MissingServletRequestParameterException::class, MethodArgumentTypeMismatchException::class, HttpMessageNotReadableException::class)
    fun malformedRequest(e: Exception, request: HttpServletRequest): ProblemDetail =
        problem(HttpStatus.BAD_REQUEST, e.message?.lineSequence()?.firstOrNull(), request)

    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun beanValidation(e: MethodArgumentNotValidException, request: HttpServletRequest): ProblemDetail {
        val detail = e.bindingResult.fieldErrors.joinToString("; ") { "${it.field}: ${it.defaultMessage}" }
        return problem(HttpStatus.BAD_REQUEST, detail, request)
    }

    @ExceptionHandler(SessionHeaderMissingException::class)
    fun headerMissing(e: SessionHeaderMissingException, request: HttpServletRequest): ProblemDetail =
        problem(HttpStatus.PRECONDITION_REQUIRED, e.message, request)

    @ExceptionHandler(SessionClosedException::class)
    fun sessionClosed(e: SessionClosedException, request: HttpServletRequest): ProblemDetail =
        problem(HttpStatus.CONFLICT, e.message, request)

    @ExceptionHandler(IllegalStateException::class)
    fun conflict(e: IllegalStateException, request: HttpServletRequest): ProblemDetail = when (e) {
        is SessionNotBoundException, is MissingParameterException -> {
            log.error("Configuration error on {}", request.requestURI, e)
            problem(HttpStatus.INTERNAL_SERVER_ERROR, e.message, request)
        }
        else -> problem(HttpStatus.CONFLICT, e.message, request)
    }

    @ExceptionHandler(Exception::class)
    fun unexpected(e: Exception, request: HttpServletRequest): ProblemDetail {
        log.error("Unhandled error on {} {}", request.method, request.requestURI, e)
        return problem(HttpStatus.INTERNAL_SERVER_ERROR, "Unexpected error", request)
    }

    private fun problem(status: HttpStatus, detail: String?, request: HttpServletRequest): ProblemDetail =
        ProblemDetail.forStatusAndDetail(status, detail ?: status.reasonPhrase).apply {
            title = status.reasonPhrase
            instance = URI.create(request.requestURI)
        }
}
