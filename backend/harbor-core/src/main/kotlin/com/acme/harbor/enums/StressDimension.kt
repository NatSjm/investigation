package com.acme.harbor.enums

/**
 * Dimension of the stress test table and chart (`GET /session/stress-test?dimension=`): city hubs for
 * Product 1, transport modes for Product 2; the page toggle may ask for the other one.
 */
enum class StressDimension(val dimensionKind: DimensionKind) {
    CITY(DimensionKind.CITY),
    TRANSPORT_MODE(DimensionKind.TRANSPORT_MODE);

    companion object {
        fun of(kind: DimensionKind): StressDimension = entries.first { it.dimensionKind == kind }

        /** Default dimension of a product group (the one stored in `stress_test_result`). */
        fun defaultFor(productGroup: ProductGroup): StressDimension = of(productGroup.dimensionKind)
    }
}
