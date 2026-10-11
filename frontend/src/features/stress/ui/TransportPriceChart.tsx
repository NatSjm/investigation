import { useMemo } from 'react';
import { LineChart } from '@/shared/charts/LineChart';
import { formatPeriod } from '@/shared/utils/months';
import type { StressScenarioResult } from '../stress.types';

export interface TransportPriceChartProps {
  scenarios: StressScenarioResult[];
  /** Optional baseline transport price per month, drawn dashed. */
  baseline?: Array<{ period: string; value: number }>;
  height?: number;
}

/**
 * Transport price over time, one line per scenario (plus the dashed baseline when provided).
 * The scenario path is read from `StressTestRow.scenarioTransportPrice`, which is the same for every
 * dimension value of a month; rows without it are skipped.
 */
export function TransportPriceChart({ scenarios, baseline, height = 260 }: TransportPriceChartProps) {
  const { data, series } = useMemo(() => {
    const rows = new Map<string, Record<string, number | string>>();
    const put = (key: string, period: string, value: number) => {
      const row = rows.get(period) ?? { period };
      row[key] = value;
      rows.set(period, row);
    };
    for (const p of baseline ?? []) put('baseline', p.period, p.value);
    for (const s of scenarios) {
      for (const r of s.rows) {
        if (r.scenarioTransportPrice !== undefined) put(s.scenarioId, r.period, r.scenarioTransportPrice);
      }
    }
    const lines = scenarios.map((s) => ({ key: s.scenarioId, label: s.scenarioName }));
    if (baseline?.length) lines.unshift({ key: 'baseline', label: 'Baseline' });
    return {
      data: [...rows.values()].sort((a, b) => String(a.period).localeCompare(String(b.period))),
      series: lines.map((l) => ({ ...l, dashed: l.key === 'baseline' })),
    };
  }, [scenarios, baseline]);

  if (scenarios.length === 0) return <p className="hint">Run the stress test to see transport prices per scenario.</p>;

  return (
    <figure className="transport-price-chart">
      <figcaption>Transport price per scenario</figcaption>
      <LineChart data={data} series={series} height={height} xFormatter={(p) => formatPeriod(p, 'short')} />
    </figure>
  );
}
