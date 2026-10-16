import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import type { Session } from '@/types/meetings';
import { formatDateTime, formatPctChange } from '@/utils/format';
import { useScenarios, useScenarioMutations } from '@/pages/ScenariosPage/hook/useScenarios';
import { useBaselinePrices } from '@/pages/shared/hook/useBaselinePrices';
import { ScenarioEditor } from '@/pages/ScenariosPage/components/ScenarioEditor';
import type { Scenario, ScenarioRequest } from '@/types/market';

type EditorState = { mode: 'closed' } | { mode: 'new' } | { mode: 'edit'; scenario: Scenario };

/**
 * `/session/:sessionId/scenarios` - second meeting step: list of scenarios of the session,
 * baseline curve info and the editor to add / change / remove scenarios.
 * @docs MKT-001
 */
export function ScenariosPage() {
  const session = useOutletContext<Session>();
  const [editor, setEditor] = useState<EditorState>({ mode: 'closed' });
  const scenarios = useScenarios();
  const baseline = useBaselinePrices();
  const { create, update, remove } = useScenarioMutations();

  const save = async (request: ScenarioRequest) => {
    if (editor.mode === 'edit') await update.mutateAsync({ scenarioId: editor.scenario.scenarioId, body: request });
    else await create.mutateAsync(request);
    setEditor({ mode: 'closed' });
  };

  const removeScenario = async (s: Scenario) => {
    if (window.confirm(`Delete scenario "${s.name}"?`)) await remove.mutateAsync(s.scenarioId);
  };

  return (
    <section className="page scenarios">
      <header className="toolbar">
        <h2>Market scenarios</h2>
        {baseline.data && (
          <span className="hint">
            Baseline {baseline.data.corridor} as of {formatDateTime(baseline.data.asOf)} ({baseline.data.points.length} months)
          </span>
        )}
        <button type="button" className="primary" onClick={() => setEditor({ mode: 'new' })} disabled={session.status !== 'OPEN'}>
          New scenario
        </button>
      </header>

      {scenarios.isLoading && <p>Loading scenarios...</p>}
      {scenarios.error && <p role="alert">Scenarios could not be loaded.</p>}
      <ul className="scenario-list">
        {(scenarios.data ?? []).map((s) => (
          <li key={s.scenarioId} className={editor.mode === 'edit' && editor.scenario.scenarioId === s.scenarioId ? 'selected' : undefined}>
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
            <div className="row-actions">
              <button type="button" className="link" onClick={() => setEditor({ mode: 'edit', scenario: s })}>
                Edit
              </button>
              <button type="button" className="link" onClick={() => removeScenario(s)} disabled={remove.isPending}>
                Delete
              </button>
            </div>
          </li>
        ))}
        {scenarios.data?.length === 0 && <li className="empty">No scenarios yet - add one to run the stress test.</li>}
      </ul>

      {editor.mode !== 'closed' && (
        <ScenarioEditor
          scenario={editor.mode === 'edit' ? editor.scenario : undefined}
          baseline={baseline.data?.points ?? []}
          horizonMonths={session.horizonMonths}
          pending={create.isPending || update.isPending}
          onSave={save}
          onCancel={() => setEditor({ mode: 'closed' })}
        />
      )}
    </section>
  );
}
