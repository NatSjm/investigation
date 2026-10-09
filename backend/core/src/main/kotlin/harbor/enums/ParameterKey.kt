package harbor.enums

/** Parameter keys as stored in `parameter_set.key` (BLUEPRINT.md section 3.4), with their documented defaults. */
enum class ParameterKey(val key: String) {
    ROLE_MIN_VOLUME("role.min_volume"),
    ROLE_IMPORTER_THRESHOLD("role.importer_threshold"),
    ROLE_EXPORTER_THRESHOLD("role.exporter_threshold"),
    TARIFF_RATE("tariff.rate"),
    HANDLING_COST("handling.cost"),
    TRANSPORT_COST("transport.cost"),
    COVER_DEFAULT_PREMIUM_RATE("cover.default_premium_rate"),
    PROJECTION_HORIZON_MONTHS_DEFAULT("projection.horizon_months_default"),
    STRESS_ROUNDING_SCALE("stress.rounding_scale"),
    PEER_SCALING_DEFAULT("peer.scaling_default");

    companion object {
        fun fromKey(key: String): ParameterKey? = entries.firstOrNull { it.key == key }
    }
}
