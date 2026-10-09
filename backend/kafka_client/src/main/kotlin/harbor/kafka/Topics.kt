package harbor.kafka

/**
 * Kafka topic names (BLUEPRINT.md section 3.1). Declared once here and referenced by the producers and the
 * `@KafkaListener(topics = [Topics.X], groupId = "harbor-<context>")` consumers in `core/.../harbor/event/`.
 * The AsyncAPI description lives in `core/src/main/resources/openapi/harbor-events.yaml`.
 */
object Topics {
    /** Produced by MovementsLoadedPublisher; consumed by Product1ProjectionRefreshListener and Product2ProjectionRefreshListener. */
    const val MOVEMENTS_LOADED = "harbor.imports.movements-loaded"

    /** Produced by the external market-data service; consumed by MarketPricesListener. */
    const val PRICES_UPDATED = "harbor.market.prices-updated"

    /** Produced by SessionEventsPublisher; consumed by ReportSessionClosedListener and ClientRoleSessionClosedListener. */
    const val SESSION_CLOSED = "harbor.meetings.session-closed"

    /** Produced by ReportRenderRequester; consumed by the external document-service. */
    const val REPORT_RENDER_REQUESTED = "harbor.reports.render-requested"

    /** Produced by the external document-service; consumed by ReportRenderedListener. */
    const val REPORT_RENDERED = "harbor.reports.rendered"
}
