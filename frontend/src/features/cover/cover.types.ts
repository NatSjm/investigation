/**
 * View-model types for cover. Mirror `CoverSummary`, `CoverQuoteRequest`, `CoverQuote`, `CoverPolicy`
 * from the contract (`cover` module, `CoverController`; calculation `cover_ratio`).
 * @docs COV-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type PriceBasis = components['schemas']['PriceBasis'];

/** Cover ratio of one sub-product in one month: `coveredValue / totalValue` (0 when total = 0). */
export interface CoverSummaryRow {
  period: string;
  subProduct: string;
  coveredValue: number;
  totalValue: number;
  coverRatio: number;
}

export interface CoverSummary {
  priceBasis: PriceBasis;
  rows: CoverSummaryRow[];
}

export interface CoverQuoteRequest {
  subProduct?: string;
  uncoveredValue: number;
  periodFrom: string;
  periodTo: string;
}

export interface CoverQuote {
  quoteId: string;
  uncoveredValue: number;
  premium: number;
  providerRef: string;
  requestedAt: string;
}

export interface CoverPolicy {
  policyId: string;
  productGroup: ProductGroup;
  subProduct: string;
  coveredShare: number;
  premiumRate: number;
  validFrom: string;
  validTo: string;
}

/** Sum of `totalValue - coveredValue` over the rows (optionally one sub-product); input of a quote request. */
export function uncoveredValue(rows: CoverSummaryRow[], subProduct?: string): number {
  return rows
    .filter((r) => !subProduct || r.subProduct === subProduct)
    .reduce((sum, r) => sum + Math.max(0, r.totalValue - r.coveredValue), 0);
}
