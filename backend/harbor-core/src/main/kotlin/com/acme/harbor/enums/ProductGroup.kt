package com.acme.harbor.enums

/**
 * The two product groups. Wire values are those of the OpenAPI contract (`openapi/harbor-api.yaml`) and of the
 * Kafka payloads; the enum names are stored in the database columns, so neither may be renamed.
 */
enum class ProductGroup(
    val wireValue: String,
    val corridor: String,
    val priceBases: List<PriceBasis>,
    val subProducts: List<String>,
) {
    PRODUCT1("product1", "VLD-NRL", listOf(PriceBasis.VLD, PriceBasis.NRL), listOf("P1-STD", "P1-PRM", "P1-ECO")),
    PRODUCT2("product2", "CST-MRD", listOf(PriceBasis.CST, PriceBasis.MRD), listOf("P2-S", "P2-M", "P2-L"));

    /** Primary breakdown dimension of the overview page. */
    val dimensionKind: DimensionKind
        get() = if (this == PRODUCT1) DimensionKind.CITY else DimensionKind.TRANSPORT_MODE

    companion object {
        /** Known city hubs of Product 1 (Product 2 movements carry cities as well, for the overview table). */
        val PRODUCT1_CITIES: List<String> = listOf("Aldmoor", "Brightwater", "Carrow", "Dunmere")

        fun fromWire(value: String): ProductGroup =
            entries.firstOrNull { it.wireValue.equals(value, ignoreCase = true) || it.name.equals(value, ignoreCase = true) }
                ?: throw IllegalArgumentException("Unknown product group '$value'")
    }
}
