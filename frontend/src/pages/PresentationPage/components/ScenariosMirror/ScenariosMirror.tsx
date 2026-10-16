import { useScenarios } from '@/pages/ScenariosPage/hook/useScenarios';
import { useBaselinePrices } from '@/pages/shared/hook/useBaselinePrices';
import { formatDateTime, formatPctChange } from '@/utils/format';

/**
 * Read-only mirror of the scenarios step: baseline info and the scenario list with their shocks.
 * No editor, no create / edit / delete actions.
 * @docs PRS-001
 */
export function ScenariosMirror() {
  const scenarios = useScenarios();
  const baseline = useBaselinePrices();

  return (
    <section className="page scenarios">
      <header className="toolbar">
        <h2>Market scenarios</h2>
        {baseline.data && (
          <span className="hint">
            Baseline {baseline.data.corridor} as of {formatDateTime(baseline.data.asOf)} ({baseline.data.points.length} months)
          </span>
        )}
      </header>
      {scenarios.isLoading && <p>Loading scenarios...</p>}
      {scenarios.error && <p role="alert">Scenarios are not available.</p>}
      <ul className="scenario-list">
        {(scenarios.data ?? []).map((s) => (
          <li key={s.scenarioId}>
            <div>
              <strong>{s.name}</strong> <span className={`kind kind-${s.kind.toLowerCase()}`}>{s.kind}</span>
              <ul className="shock-summary">
                {s.shocks.map((sh, i) => (
                  <li key={i}>
                    from month {sh.fromMonth}: price {formatPctChange(sh.priceChangePct)}, transport {formatPctChange(sh.transportChangePct)}
                  </li>
                ))}
                {s.shocks.length === 0 && <li>no shocks (baseline)</li>}
              </ul>
            </div>
          </li>
        ))}
        {scenarios.data?.length === 0 && <li className="empty">No scenarios yet.</li>}
      </ul>
    </section>
  );
}
