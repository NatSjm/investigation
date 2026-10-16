/**
 * Month grid helpers. A period is an ISO month string `YYYY-MM` - the same key the backend
 * (`harbor-core/src/main/kotlin/com/acme/harbor/utils/MonthGrid.kt`) uses for every monthly table, so rows join on it without conversion.
 */

export type Period = string;

const PERIOD_RE = /^(\d{4})-(0[1-9]|1[0-2])$/;

export function isPeriod(value: string): value is Period {
  return PERIOD_RE.test(value);
}

export function parsePeriod(period: Period): { year: number; month: number } {
  const m = PERIOD_RE.exec(period);
  if (!m) throw new Error(`Invalid period '${period}', expected YYYY-MM`);
  return { year: Number(m[1]), month: Number(m[2]) };
}

export function toPeriod(year: number, month: number): Period {
  return `${year}-${String(month).padStart(2, '0')}`;
}

/** Period of a date (local time); defaults to today. */
export function currentPeriod(date: Date = new Date()): Period {
  return toPeriod(date.getFullYear(), date.getMonth() + 1);
}

export function addMonths(period: Period, offset: number): Period {
  const { year, month } = parsePeriod(period);
  const index = year * 12 + (month - 1) + offset;
  return toPeriod(Math.floor(index / 12), (index % 12) + 1);
}

/**
 * Consecutive periods starting at `from`, `horizon` entries long (planning horizon 12-60 months).
 * `monthGrid('2026-11', 3)` -> `['2026-11', '2026-12', '2027-01']`.
 */
export function monthGrid(from: Period, horizon: number): Period[] {
  if (!Number.isInteger(horizon) || horizon < 0) throw new Error(`Invalid horizon ${horizon}`);
  return Array.from({ length: horizon }, (_, i) => addMonths(from, i));
}

/**
 * The projection grid of a session exactly as the backend builds it (`MonthGrid.startingAfter`): it starts with
 * the month after the current one (the current month is not a full actual month yet) and spans `horizon` months.
 * Movements entered for a month outside this grid are rejected by the backend with 400.
 */
export function projectionGrid(horizon: number, today: Date = new Date()): Period[] {
  return monthGrid(addMonths(currentPeriod(today), 1), horizon);
}

/** Whole months between two periods (`to - from`), negative when `to` is earlier. */
export function monthsBetween(from: Period, to: Period): number {
  const a = parsePeriod(from);
  const b = parsePeriod(to);
  return (b.year - a.year) * 12 + (b.month - a.month);
}

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** Display label: `formatPeriod('2026-03')` -> `'Mar 2026'`; `short` -> `'Mar 26'`. */
export function formatPeriod(period: Period, style: 'long' | 'short' = 'long'): string {
  if (!isPeriod(period)) return period;
  const { year, month } = parsePeriod(period);
  const name = MONTH_NAMES[month - 1];
  return style === 'short' ? `${name} ${String(year).slice(2)}` : `${name} ${year}`;
}

/** Groups any monthly rows by period, preserving grid order and filling missing months with `[]`. */
export function byPeriod<T extends { period: Period }>(grid: Period[], rows: T[]): Map<Period, T[]> {
  const map = new Map<Period, T[]>(grid.map((p) => [p, [] as T[]]));
  for (const row of rows) {
    const bucket = map.get(row.period);
    if (bucket) bucket.push(row);
  }
  return map;
}
