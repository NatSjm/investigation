import { useMemo, useState } from 'react';
import { formatDateTime, formatRatio, formatValue } from '@/utils/format';
import { useCoverSummary } from '@/pages/shared/hook/useCoverSummary';
import { useCoverQuote } from '@/pages/shared/hook/useCoverQuote';
import { uncoveredValue, type CoverQuoteRequest } from '@/types/cover';

export interface CoverQuotePanelProps {
  /** Suffix for monetary values; omitted while the contract does not provide a price basis. */
  priceBasis?: string;
  subProducts: readonly string[];
}

/**
 * Embedded in the product overview pages: current cover position over the horizon and a
 * one-click quote request for the uncovered part (per sub-product or all). The request names the
 * sub-products and period range; the backend computes the uncovered value itself.
 * @docs COV-001
 */
export function CoverQuotePanel({ priceBasis, subProducts }: CoverQuotePanelProps) {
  const [subProduct, setSubProduct] = useState<string>('');
  const summary = useCoverSummary();
  const quote = useCoverQuote();

  const months = summary.data?.months ?? [];
  const uncovered = useMemo(() => uncoveredValue(months, subProduct || undefined), [months, subProduct]);
  const total = months.filter((r) => !subProduct || r.subProduct === subProduct).reduce((s, r) => s + r.totalValue, 0);
  const periods = months.map((r) => r.period).sort();

  const request = () => {
    const body: CoverQuoteRequest = { subProducts: subProduct ? [subProduct] : [...subProducts] };
    if (periods.length > 0) {
      body.fromPeriod = periods[0];
      body.toPeriod = periods[periods.length - 1];
    }
    quote.mutate(body);
  };

  return (
    <section className="cover-quote-panel">
      <h3>Cover</h3>
      {summary.isLoading && <p>Loading cover summary...</p>}
      {summary.error && <p role="alert">Cover summary could not be loaded.</p>}
      <label>
        Sub-product
        <select value={subProduct} onChange={(e) => setSubProduct(e.target.value)}>
          <option value="">All</option>
          {subProducts.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
      </label>
      <dl>
        <dt>Total value (horizon)</dt>
        <dd>{formatValue(total, priceBasis)}</dd>
        <dt>Uncovered value</dt>
        <dd>{formatValue(uncovered, priceBasis)}</dd>
        <dt>Cover ratio</dt>
        <dd>{formatRatio(total > 0 ? (total - uncovered) / total : 0)}</dd>
      </dl>
      <button type="button" disabled={uncovered <= 0 || quote.isPending} onClick={request}>
        {quote.isPending ? 'Requesting quote...' : 'Request quote for uncovered part'}
      </button>
      {quote.data && (
        <p className="quote-result">
          Quote {quote.data.providerRef ?? quote.data.quoteId}: premium {formatValue(quote.data.premium, priceBasis)} (
          {formatDateTime(quote.data.requestedAt)})
        </p>
      )}
      {quote.error && <p role="alert">The cover provider did not return a quote.</p>}
    </section>
  );
}
