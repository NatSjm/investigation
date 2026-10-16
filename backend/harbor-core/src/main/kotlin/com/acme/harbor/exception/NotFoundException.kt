package com.acme.harbor.exception

/** A requested entity (client, session, scenario, report, ...) does not exist -> HTTP 404. */
class NotFoundException(entity: String, id: Any) : RuntimeException("$entity '$id' not found")
