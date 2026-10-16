/**
 * View-model types for cover. Aliases of `CoverSummary`, `CoverMonth`, `CoverQuoteRequest`, `CoverQuote`, `CoverPolicy`
 * from the contract (`cover` module, `CoverController`; calculation `cover_ratio`).
 * @docs COV-001
 */
import type { components } from '@/services/openapi/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type PriceBasis = components['schemas']['PriceBasis'];

/** Cover ratio of one sub-product (or `ALL`) in one month (`CoverMonth`): `coveredValue / totalValue` (0 when total = 0). */
export type CoverSummaryRow = components['schemas']['CoverMonth'];

export type CoverSummary = components['schemas']['CoverSummary'];

export type CoverQuoteRequest = components['schemas']['CoverQuoteRequest'];

export type CoverQuote = components['schemas']['CoverQuote'];

export type CoverPolicy = components['schemas']['CoverPolicy'];

/** Sum of `totalValue - coveredValue` over the rows (optionally one sub-product); shown next to the quote button. */
export function uncoveredValue(rows: CoverSummaryRow[], subProduct?: string): number {
  return rows
    .filter((r) => !subProduct || r.subProduct === subProduct)
    .reduce((sum, r) => sum + Math.max(0, r.totalValue - r.coveredValue), 0);
}
