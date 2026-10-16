package com.acme.harbor.enums

/** Price basis = the country side of a corridor whose price list applies (imitates two currencies per product). */
enum class PriceBasis(val country: String) {
    VLD("Veldora"),
    NRL("Norland"),
    CST("Castra"),
    MRD("Meridia"),
}
