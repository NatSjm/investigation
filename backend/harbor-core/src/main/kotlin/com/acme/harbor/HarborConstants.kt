package com.acme.harbor

/** Application-wide constants: the names and paths that the contract, the filters and the controllers share. */
object HarborConstants {
    const val APPLICATION_NAME = "harbor-backend"
    const val API_BASE_PATH = "/api/v1"
    const val SESSION_PATH_PREFIX = "$API_BASE_PATH/session/"
    const val SESSION_HEADER = "X-Harbor-Session"
}
