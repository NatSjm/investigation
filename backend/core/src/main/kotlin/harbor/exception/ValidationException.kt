package harbor.exception

/** Request content violates a business rule checked by a `harbor.validator` class -> HTTP 400. */
class ValidationException(message: String) : RuntimeException(message) {

    companion object {
        /** Throws a [ValidationException] with [message] unless [condition] holds. */
        inline fun check(condition: Boolean, message: () -> String) {
            if (!condition) throw ValidationException(message())
        }
    }
}
