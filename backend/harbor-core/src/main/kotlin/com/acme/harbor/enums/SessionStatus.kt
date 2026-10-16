package com.acme.harbor.enums

/** Lifecycle of a meeting session; only OPEN sessions accept `/session` sub-path requests. */
enum class SessionStatus { OPEN, CLOSED }
