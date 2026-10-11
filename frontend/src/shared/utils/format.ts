/**
 * Number formatting shared by tables and charts. Values are shown in the session's price basis
 * (`VLD`/`NRL` for Product 1, `CST`/`MRD` for Product 2) - the two countries of a corridor each
 * carry their own basis, so the basis code is always rendered next to the amount.
 */

export type PriceBasis = 'VLD' | 'NRL' | 'CST' | 'MRD';

const qtyFormatter = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 });
const valueFormatter = new Intl.NumberFormat('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pctFormatter = new Intl.NumberFormat('en-GB', { style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 });

/** Quantities (units moved): integers with thousands separators; `formatQty(12345.6)` -> `'12,346'`. */
export function formatQty(quantity: number | null | undefined): string {
  if (quantity === null || quantity === undefined || Number.isNaN(quantity)) return '-';
  return qtyFormatter.format(quantity);
}

/**
 * Monetary values with the price basis suffix; `formatValue(1234.5, 'VLD')` -> `'1,234.50 VLD'`.
 * The contract does not yet carry a price basis on any response, so callers may omit it: `formatValue(1234.5)` -> `'1,234.50'`.
 */
export function formatValue(value: number | null | undefined, priceBasis?: PriceBasis | string): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '-';
  return priceBasis ? `${valueFormatter.format(value)} ${priceBasis}` : valueFormatter.format(value);
}

/** Signed variant used for deltas and exposure: `+1,200.00 VLD` / `-300.00 VLD`. */
export function formatSignedValue(value: number | null | undefined, priceBasis?: PriceBasis | string): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '-';
  const sign = value > 0 ? '+' : '';
  return `${sign}${formatValue(value, priceBasis)}`;
}

/** Ratios in `[0, 1]` as percentages; `formatRatio(0.8234)` -> `'82.3%'`. */
export function formatRatio(ratio: number | null | undefined): string {
  if (ratio === null || ratio === undefined || Number.isNaN(ratio)) return '-';
  return pctFormatter.format(ratio);
}

/** Percentage change inputs stored as fractions (0.05 -> `+5.0%`). */
export function formatPctChange(fraction: number): string {
  const sign = fraction > 0 ? '+' : '';
  return `${sign}${pctFormatter.format(fraction)}`;
}

/** ISO timestamp -> `2026-10-09 14:05`. */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '-';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}
