import { useMemo, useState } from 'react';
import { formatDateTime, formatRatio, formatValue } from '@/shared/utils/format';
import { useCoverSummary } from '../api/useCoverSummary';
import { useCoverQuote } from '../api/useCoverQuote';
import { uncoveredValue } from '../cover.types';

export interface CoverQuotePanelProps {
  priceBasis: string;
  subProducts: readonly string[];
}

/**
 * Embedded in the product overview pages: current cover position over the horizon and a
 * one-click quote request for the uncovered part (per sub-product or all).
 */
export function CoverQuotePanel({ priceBasis, subProducts }: CoverQuotePanelProps) {
  const [subProduct, setSubProduct] = useState<string>('');
  const summary = useCoverSummary();
  const quote = useCoverQuote();

  const rows = summary.data?.rows ?? [];
  const uncovered = useMemo(() => uncoveredValue(rows, subProduct || undefined), [rows, subProduct]);
  const total = rows.filter((r) => !subProduct || r.subProduct === subProduct).reduce((s, r) => s + r.totalValue, 0);
  const periods = rows.map((r) => r.period).sort();

  const request = () =>
    quote.mutate({
      subProduct: subProduct || undefined,
      uncoveredValue: uncovered,
      periodFrom: periods[0] ?? '',
      periodTo: periods[periods.length - 1] ?? '',
    });

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
          Quote {quote.data.providerRef}: premium {formatValue(quote.data.premium, priceBasis)} ({formatDateTime(quote.data.requestedAt)})
        </p>
      )}
      {quote.error && <p role="alert">The cover provider did not return a quote.</p>}
    </section>
  );
}
