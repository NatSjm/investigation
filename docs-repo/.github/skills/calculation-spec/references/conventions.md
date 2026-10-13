# Conventions vocabulary

## Rounding
`HALF_EVEN` (default for money, scale 2), `HALF_UP`, `DOWN`; ratios scale 4. Say **where** rounding happens
(per month vs at the end of the cumulative sum).

## Month grid
`period` = first day of the month (`LocalDate`), horizon = `projection.horizon_months_default` (24) unless the
session config overrides (12-60). "Last 12 full months" excludes the current month.

## Quantities, values, price basis
`quantity` in product units; `unit_price` in the row's `price_basis` (`VLD|NRL` for Product 1, `CST|MRD` for
Product 2); `value = quantity x unit_price x price_index(period)`; `landed_cost` adds tariff, handling and transport.

## Direction and role
`direction = IN | OUT` per movement row; role `IMPORTER | EXPORTER | MIXED | UNDETERMINED` per client and product
group; sign convention in the stress test: importer `+1`, exporter `-1`, MIXED uses net uncovered quantity.

## Cover
`covered_share` in [0, 1] per policy; a policy with `sub_product = null` applies to all sub-products of the group;
`uncovered_quantity = quantity x (1 - covered_share)`.

## Scenarios
Baseline curve from `baseline_price` (fed by market-data); shocks `{fromMonth, priceChangePct, transportChangePct}`
compound multiplicatively from `fromMonth` onwards; `BASELINE` scenario has no shocks.

## Parameters
Keys, seeded defaults per scope, readers and the validator are generated into `generated/be/parameters.md`; cite keys$1exactly as there. The `## Parameters` table of the calculation owns the meaning of a key (unit, bound, formula it feeds);$1the admin spec `ADM-001` owns scope, versioning and validation and maps every key to its owner.$1Quote the key, not the number, unless the number is in the worked example.
