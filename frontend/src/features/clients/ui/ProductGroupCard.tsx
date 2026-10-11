import { LineChart } from '@/shared/charts/LineChart';
import { formatQty, formatRatio, formatValue } from '@/shared/utils/format';
import { PRODUCT_GROUP_LABEL, type ProductGroupIndicators } from '../clients.types';

export interface ProductGroupCardProps {
  indicators: ProductGroupIndicators;
  busy?: boolean;
  onStartMeeting: () => void;
  onPrepare: () => void;
}

const ROLE_LABEL: Record<ProductGroupIndicators['role'], string> = {
  IMPORTER: 'Importer',
  EXPORTER: 'Exporter',
  MIXED: 'Mixed',
  UNDETERMINED: 'Undetermined',
};

/**
 * Key indicators for one product group + sparkline (last 12 months) + session start buttons.
 * The contract carries no price basis on the indicators, so `value12m` is shown without a basis suffix.
 */
export function ProductGroupCard({ indicators, busy, onStartMeeting, onPrepare }: ProductGroupCardProps) {
  const sparkData = indicators.sparkline.map((p) => ({ period: p.period, value: p.value }));

  return (
    <article className="product-card" aria-label={PRODUCT_GROUP_LABEL[indicators.productGroup]}>
      <header>
        <h2>{PRODUCT_GROUP_LABEL[indicators.productGroup]}</h2>
        <span className={`role role-${indicators.role.toLowerCase()}`}>{ROLE_LABEL[indicators.role]}</span>
      </header>
      <dl className="indicators">
        <dt>Volume (12m)</dt>
        <dd>{formatQty(indicators.volume12m)}</dd>
        <dt>Value (12m)</dt>
        <dd>{formatValue(indicators.value12m)}</dd>
        <dt>Cover ratio</dt>
        <dd>{formatRatio(indicators.coverRatio)}</dd>
        <dt>Open sessions</dt>
        <dd>{indicators.openSessions}</dd>
      </dl>
      <div className="sparkline" aria-hidden="true">
        <LineChart data={sparkData} series={[{ key: 'value', label: 'Monthly quantity' }]} height={80} />
      </div>
      <footer className="actions">
        <button type="button" className="primary" disabled={busy} onClick={onStartMeeting}>
          Start meeting
        </button>
        <button type="button" disabled={busy} onClick={onPrepare}>
          Prepare
        </button>
      </footer>
    </article>
  );
}
