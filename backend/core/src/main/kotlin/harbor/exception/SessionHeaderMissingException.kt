package harbor.exception

/** A `/session/**` request arrived without the `X-Harbor-Session` header -> HTTP 428. */
class SessionHeaderMissingException(headerName: String, path: String) :
    RuntimeException("Header $headerName is required for $path")
