import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useSessionStore } from '@/services/api/sessionStore';
import type { Session } from '@/types/meetings';
import { useBaselinePrices } from '@/pages/shared/hook/useBaselinePrices';
import { usePresentationPublisher } from '@/components/hook/usePresentationPublisher';
import { formatDateTime } from '@/utils/format';
import { useStressTest } from '@/pages/StressTestPage/hook/useStressTest';
import { useRunStressTest } from '@/pages/StressTestPage/hook/useRunStressTest';
import { StressTable } from '@/pages/StressTestPage/components/StressTable';
import { TransportPriceChart } from '@/pages/StressTestPage/components/TransportPriceChart';
import { DimensionToggle } from '@/pages/StressTestPage/components/DimensionToggle';
import { defaultDimension, type Dimension } from '@/types/stress';

/**
 * `/session/:sessionId/stress-test` - third meeting step: one monthly table per scenario,
 * transport price chart per scenario and the dimension toggle (city / transport mode).
 * The toggle defaults to the session's product group: CITY for product1, TRANSPORT_MODE for product2.
 * @docs STR-001
 */
export function StressTestPage() {
  const session = useOutletContext<Session>();
  const productGroup = useSessionStore((s) => s.productGroup);
  const [dimension, setDimension] = useState<Dimension>(() => defaultDimension(productGroup));

  useEffect(() => {
    setDimension(defaultDimension(productGroup));
  }, [productGroup]);

  const result = useStressTest(dimension);
  const run = useRunStressTest();
  const baseline = useBaselinePrices();
  const publish = usePresentationPublisher(session.sessionId);

  // Mirror the breakdown dimension to the client screen (`view` message).
  useEffect(() => {
    publish({ type: 'view', stress: { dimension } });
  }, [dimension, publish]);

  const baselineTransport = baseline.data?.points.map((p) => ({ period: p.period, value: p.transportPrice }));

  return (
    <section className="page stress-test">
      <header className="toolbar">
        <h2>Stress test</h2>
        <DimensionToggle value={dimension} onChange={setDimension} disabled={run.isPending} />
        <div className="actions">
          <button type="button" className="primary" disabled={run.isPending || session.status !== 'OPEN'} onClick={() => run.mutate()}>
            {run.isPending ? 'Computing...' : 'Run stress test'}
          </button>
          {result.data?.computedAt && <span className="hint">computed {formatDateTime(result.data.computedAt)}</span>}
        </div>
      </header>

      {result.isLoading && <p>Loading results...</p>}
      {result.error && <p role="alert">Stress test results could not be loaded.</p>}
      {run.error && <p role="alert">The stress test could not be computed.</p>}

      <TransportPriceChart scenarios={result.data?.scenarios ?? []} baseline={baselineTransport} />

      {(result.data?.scenarios ?? []).map((s) => (
        <StressTable key={s.scenarioId} scenario={s} dimension={dimension} />
      ))}
      {result.data && result.data.scenarios.length === 0 && (
        <p className="hint">No scenarios defined - add scenarios in the previous step, then run the stress test.</p>
      )}
    </section>
  );
}
