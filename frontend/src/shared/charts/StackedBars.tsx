import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export interface BarSeries {
  key: string;
  label: string;
  color?: string;
}

export interface StackedBarsProps {
  /** Rows shaped `{ period: '2026-01', <seriesKey>: number, ... }`. */
  data: Array<Record<string, number | string>>;
  series: BarSeries[];
  xKey?: string;
  height?: number;
  yFormatter?: (value: number) => string;
  xFormatter?: (value: string) => string;
}

const palette = ['#1d4ed8', '#60a5fa', '#bfdbfe', '#9ca3af', '#fbbf24', '#34d399'];

/** Thin recharts wrapper: stacked bars per month (one stack segment per series). */
export function StackedBars({ data, series, xKey = 'period', height = 260, yFormatter, xFormatter }: StackedBarsProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
        <XAxis dataKey={xKey} tickFormatter={xFormatter} minTickGap={24} />
        <YAxis tickFormatter={yFormatter} width={72} />
        <Tooltip formatter={(v: unknown) => (yFormatter && typeof v === 'number' ? yFormatter(v) : String(v))} labelFormatter={xFormatter} />
        <Legend />
        {series.map((s, i) => (
          <Bar key={s.key} dataKey={s.key} name={s.label} stackId="stack" fill={s.color ?? palette[i % palette.length]} isAnimationActive={false} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
