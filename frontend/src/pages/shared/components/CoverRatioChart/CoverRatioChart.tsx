import { useMemo } from 'react';
import { LineChart } from '@/components/LineChart';
import { formatRatio } from '@/utils/format';
import { formatPeriod } from '@/utils/months';
import type { CoverSeries } from '@/types/product1';

export interface CoverRatioChartProps {
  /** Flat `CoverSeriesPoint[]` from the overview (one point per period x sub-product). */
  series: CoverSeries;
  height?: number;
}

/**
 * Cover ratio per month, one line per sub-product (calculation `cover_ratio`).
 * Points are pivoted into one row per period so recharts can draw them on a shared axis.
 * @docs P1-001
 */
export function CoverRatioChart({ series, height = 240 }: CoverRatioChartProps) {
  const { data, subProducts } = useMemo(() => {
    const byPeriod = new Map<string, Record<string, number | string>>();
    const subProducts: string[] = [];
    for (const p of series) {
      const row = byPeriod.get(p.period) ?? { period: p.period };
      row[p.subProduct] = p.coverRatio;
      byPeriod.set(p.period, row);
      if (!subProducts.includes(p.subProduct)) subProducts.push(p.subProduct);
    }
    return {
      data: [...byPeriod.values()].sort((a, b) => String(a.period).localeCompare(String(b.period))),
      subProducts,
    };
  }, [series]);

  if (series.length === 0) return <p className="hint">No cover policies for this product group.</p>;

  return (
    <figure className="cover-ratio-chart">
      <figcaption>Cover ratio per sub-product</figcaption>
      <LineChart
        data={data}
        series={subProducts.map((s) => ({ key: s, label: s }))}
        height={height}
        yFormatter={formatRatio}
        xFormatter={(p) => formatPeriod(p, 'short')}
      />
    </figure>
  );
}
