import { useBaselinePrices } from '@/features/market';
import { StressTable, TransportPriceChart, useStressTest, DIMENSION_LABEL, type Dimension } from '@/features/stress';
import { formatDateTime } from '@/shared/utils/format';

export interface StressMirrorProps {
  dimension: Dimension;
}

/**
 * Read-only mirror of the stress test step for the dimension the representative selected:
 * transport price chart and one table per scenario. No dimension toggle, no "Run stress test".
 * @docs PRS-001
 */
export function StressMirror({ dimension }: StressMirrorProps) {
  const result = useStressTest(dimension);
  const baseline = useBaselinePrices();
  const baselineTransport = baseline.data?.points.map((p) => ({ period: p.period, value: p.transportPrice }));

  return (
    <section className="page stress-test">
      <header className="toolbar">
        <h2>Stress test</h2>
        <span className="hint">{DIMENSION_LABEL[dimension]}</span>
        {result.data?.computedAt && <span className="hint">computed {formatDateTime(result.data.computedAt)}</span>}
      </header>
      {result.isLoading && <p>Loading results...</p>}
      {result.error && <p role="alert">Stress test results are not available.</p>}
      <TransportPriceChart scenarios={result.data?.scenarios ?? []} baseline={baselineTransport} />
      {(result.data?.scenarios ?? []).map((s) => (
        <StressTable key={s.scenarioId} scenario={s} dimension={dimension} />
      ))}
      {result.data && result.data.scenarios.length === 0 && <p className="hint">No scenarios defined yet.</p>}
    </section>
  );
}
