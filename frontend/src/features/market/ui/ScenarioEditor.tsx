import { useEffect, useState } from 'react';
import { LineChart } from '@/shared/charts/LineChart';
import { formatPeriod } from '@/shared/utils/months';
import { ShockRow } from './ShockRow';
import { scenarioPricePath, type BaselinePoint, type Scenario, type ScenarioKind, type ScenarioRequest, type Shock } from '../market.types';

export interface ScenarioEditorProps {
  scenario?: Scenario;
  baseline: BaselinePoint[];
  horizonMonths: number;
  pending?: boolean;
  onSave: (request: ScenarioRequest) => Promise<unknown> | void;
  onCancel: () => void;
}

/** Contract vocabulary: who authored the scenario (the representative is the default author in this workspace). */
const KINDS: ScenarioKind[] = ['REPRESENTATIVE', 'CLIENT'];
const DEFAULT_KIND: ScenarioKind = 'REPRESENTATIVE';
const emptyShock: Shock = { fromMonth: 1, priceChangePct: 0, transportChangePct: 0 };

/** Form for one scenario (name, kind, shocks) with a live preview of the resulting price paths. */
export function ScenarioEditor({ scenario, baseline, horizonMonths, pending, onSave, onCancel }: ScenarioEditorProps) {
  const [name, setName] = useState(scenario?.name ?? '');
  const [kind, setKind] = useState<ScenarioKind>(scenario?.kind ?? DEFAULT_KIND);
  const [shocks, setShocks] = useState<Shock[]>(scenario?.shocks ?? [{ ...emptyShock }]);

  useEffect(() => {
    setName(scenario?.name ?? '');
    setKind(scenario?.kind ?? DEFAULT_KIND);
    setShocks(scenario?.shocks ?? [{ ...emptyShock }]);
  }, [scenario]);

  const preview = scenarioPricePath(baseline, shocks).map((p) => ({
    period: p.period,
    baseline: p.price,
    scenario: p.scenarioPrice,
    transportBaseline: p.transportPrice,
    transport: p.scenarioTransportPrice,
  }));

  const valid = name.trim().length >= 3 && shocks.every((s) => s.fromMonth >= 1 && s.fromMonth <= horizonMonths);

  return (
    <form
      className="scenario-editor"
      onSubmit={(e) => {
        e.preventDefault();
        if (valid) void onSave({ name: name.trim(), kind, shocks });
      }}
    >
      <h3>{scenario ? `Edit "${scenario.name}"` : 'New scenario'}</h3>
      <div className="modal-controls">
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Transport +15% from month 6" />
        </label>
        <label>
          Kind
          <select value={kind} onChange={(e) => setKind(e.target.value as ScenarioKind)}>
            {KINDS.map((k) => (
              <option key={k}>{k}</option>
            ))}
          </select>
        </label>
      </div>
      <table className="data-table dense shocks">
        <thead>
          <tr>
            <th>#</th>
            <th>From month</th>
            <th>Price change %</th>
            <th>Transport price change %</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {shocks.map((s, i) => (
            <ShockRow
              key={i}
              index={i}
              shock={s}
              horizonMonths={horizonMonths}
              onChange={(next) => setShocks(shocks.map((x, j) => (j === i ? next : x)))}
              onRemove={() => setShocks(shocks.filter((_, j) => j !== i))}
            />
          ))}
        </tbody>
      </table>
      <button type="button" className="link" onClick={() => setShocks([...shocks, { ...emptyShock, fromMonth: Math.min(horizonMonths, shocks.length + 1) }])}>
        Add shock
      </button>
      <figure>
        <figcaption>Preview: price and transport price vs baseline</figcaption>
        <LineChart
          data={preview}
          series={[
            { key: 'baseline', label: 'Baseline price', dashed: true },
            { key: 'scenario', label: 'Scenario price' },
            { key: 'transportBaseline', label: 'Baseline transport price', dashed: true },
            { key: 'transport', label: 'Scenario transport price' },
          ]}
          xFormatter={(p) => formatPeriod(p, 'short')}
          height={220}
        />
      </figure>
      <div className="actions">
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="primary" disabled={!valid || pending}>
          {scenario ? 'Save changes' : 'Create scenario'}
        </button>
      </div>
    </form>
  );
}
