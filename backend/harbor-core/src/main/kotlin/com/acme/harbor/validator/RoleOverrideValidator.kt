package com.acme.harbor.validator

import com.acme.harbor.enums.ClientRole
import com.acme.harbor.exception.SessionClosedException
import com.acme.harbor.exception.ValidationException
import com.acme.harbor.dao.model.MeetingSession
import org.springframework.stereotype.Component

/**
 * Rules for `setRoleOverride` during a meeting:
 * - the session must still be OPEN,
 * - the role must be IMPORTER, EXPORTER or MIXED (UNDETERMINED is an algorithm outcome, not a choice),
 * - a reason is mandatory and at most [MAX_REASON_LENGTH] characters (it is shown in the role history).
 */
@Component
class RoleOverrideValidator {

    fun validate(session: MeetingSession, role: ClientRole, reason: String?) {
        if (!session.isOpen) throw SessionClosedException(session.id)
        ValidationException.check(role != ClientRole.UNDETERMINED) { "UNDETERMINED cannot be set as a manual role" }
        ValidationException.check(!reason.isNullOrBlank()) { "A reason is required for a manual role override" }
        ValidationException.check(reason!!.length <= MAX_REASON_LENGTH) { "reason must not exceed $MAX_REASON_LENGTH characters" }
    }

    companion object {
        const val MAX_REASON_LENGTH = 500
    }
}
