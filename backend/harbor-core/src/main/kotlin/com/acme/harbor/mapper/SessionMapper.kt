package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.Session
import com.acme.harbor.api.generated.model.SessionCreated
import com.acme.harbor.enums.ClientRole
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.enums.SessionKind
import com.acme.harbor.enums.SessionStatus
import com.acme.harbor.manager.MeetingManager
import java.time.ZoneOffset
import com.acme.harbor.api.generated.model.ClientRole as ApiClientRole
import com.acme.harbor.api.generated.model.ProductGroup as ApiProductGroup
import com.acme.harbor.api.generated.model.SessionKind as ApiSessionKind
import com.acme.harbor.api.generated.model.SessionStatus as ApiSessionStatus

/** Maps meeting sessions to the generated API models. */
object SessionMapper {

    fun ApiProductGroup.toDomain(): ProductGroup = ProductGroup.fromWire(value)
    fun ApiSessionKind.toDomain(): SessionKind = SessionKind.valueOf(name)
    fun ApiSessionStatus.toDomain(): SessionStatus = SessionStatus.valueOf(name)
    fun ApiClientRole.toDomain(): ClientRole = ClientRole.valueOf(name)

    fun created(view: MeetingManager.SessionView): SessionCreated = SessionCreated(sessionId = view.session.id)

    fun session(view: MeetingManager.SessionView): Session = Session(
        sessionId = view.session.id,
        clientId = view.session.clientId,
        clientName = view.clientName,
        productGroup = ApiProductGroup.valueOf(view.session.productGroup.wireValue),
        kind = ApiSessionKind.valueOf(view.session.kind.name),
        status = ApiSessionStatus.valueOf(view.session.status.name),
        representativeId = view.session.representativeId,
        startedAt = view.session.startedAt.atOffset(ZoneOffset.UTC),
        closedAt = view.session.closedAt?.atOffset(ZoneOffset.UTC),
        horizonMonths = view.config.horizonMonths,
        roleOverride = view.session.roleOverride?.let { ApiClientRole.valueOf(it.name) },
        roleOverrideReason = view.session.roleOverrideReason,
        reportRequestedAt = view.session.reportRequestedAt?.atOffset(ZoneOffset.UTC),
    )
}
