/**
 * @module cover — Cover policies and cover ratio per month per sub-product; quote for the uncovered part from the cover provider.
 * Cover position of a session: cover ratio per month and sub-product, and quotes for the uncovered part.
 * @docs COV-001
 */
export { CoverQuotePanel } from './ui/CoverQuotePanel';
export { useCoverSummary } from './api/useCoverSummary';
export { useCoverPolicies } from './api/useCoverSummary';
export { useCoverQuote } from './api/useCoverQuote';
export type { CoverSummary, CoverSummaryRow, CoverQuote, CoverQuoteRequest, CoverPolicy } from './cover.types';
export { uncoveredValue } from './cover.types';
