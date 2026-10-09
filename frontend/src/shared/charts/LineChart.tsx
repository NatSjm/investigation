import {
  CartesianGrid,
  Legend,
  Line,
  LineChart as RechartsLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export interface LineSeries {
  /** Key of the field inside each data row. */
  key: string;
  label: string;
  color?: string;
  dashed?: boolean;
}

export interface LineChartProps {
  /** Rows shaped `{ period: '2026-01', <seriesKey>: number, ... }`. */
  data: Array<Record<string, number | string>>;
  series: LineSeries[];
  xKey?: string;
  height?: number;
  yFormatter?: (value: number) => string;
  xFormatter?: (value: string) => string;
}

const palette = ['#2563eb', '#059669', '#d97706', '#dc2626', '#7c3aed', '#0891b2'];

/** Thin recharts wrapper: multi-series line chart over a month axis. */
export function LineChart({ data, series, xKey = 'period', height = 260, yFormatter, xFormatter }: LineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey={xKey} tickFormatter={xFormatter} minTickGap={24} />
        <YAxis tickFormatter={yFormatter} width={72} />
        <Tooltip formatter={(v: unknown) => (yFormatter && typeof v === 'number' ? yFormatter(v) : String(v))} labelFormatter={xFormatter} />
        {series.length > 1 && <Legend />}
        {series.map((s, i) => (
          <Line
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.label}
            stroke={s.color ?? palette[i % palette.length]}
            strokeDasharray={s.dashed ? '6 4' : undefined}
            dot={false}
            isAnimationActive={false}
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  );
}
