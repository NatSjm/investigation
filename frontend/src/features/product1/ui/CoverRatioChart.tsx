import { useMemo } from 'react';
import { LineChart } from '@/shared/charts/LineChart';
import { formatRatio } from '@/shared/utils/format';
import { formatPeriod } from '@/shared/utils/months';
import type { CoverSeries } from '../product1.types';

export interface CoverRatioChartProps {
  series: CoverSeries[];
  height?: number;
}

/**
 * Cover ratio per month, one line per sub-product (calculation `cover_ratio`).
 * Series are pivoted into one row per period so recharts can draw them on a shared axis.
 */
export function CoverRatioChart({ series, height = 240 }: CoverRatioChartProps) {
  const data = useMemo(() => {
    const byPeriod = new Map<string, Record<string, number | string>>();
    for (const s of series) {
      for (const p of s.points) {
        const row = byPeriod.get(p.period) ?? { period: p.period };
        row[s.subProduct] = p.value;
        byPeriod.set(p.period, row);
      }
    }
    return [...byPeriod.values()].sort((a, b) => String(a.period).localeCompare(String(b.period)));
  }, [series]);

  if (series.length === 0) return <p className="hint">No cover policies for this product group.</p>;

  return (
    <figure className="cover-ratio-chart">
      <figcaption>Cover ratio per sub-product</figcaption>
      <LineChart
        data={data}
        series={series.map((s) => ({ key: s.subProduct, label: s.subProduct }))}
        height={height}
        yFormatter={formatRatio}
        xFormatter={(p) => formatPeriod(p, 'short')}
      />
    </figure>
  );
}
