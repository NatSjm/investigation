import { describe, expect, it } from 'vitest';
import { addMonths, byPeriod, formatPeriod, isPeriod, monthGrid, monthsBetween, parsePeriod, projectionGrid } from './months';

describe('projectionGrid', () => {
  it('starts with the month after today and spans the horizon, like the backend MonthGrid', () => {
    expect(projectionGrid(3, new Date(2026, 9, 12))).toEqual(['2026-11', '2026-12', '2027-01']);
  });
});

describe('monthGrid', () => {
  it('produces consecutive periods across a year boundary', () => {
    expect(monthGrid('2026-11', 4)).toEqual(['2026-11', '2026-12', '2027-01', '2027-02']);
  });

  it('returns an empty grid for horizon 0', () => {
    expect(monthGrid('2026-01', 0)).toEqual([]);
  });

  it('rejects negative or fractional horizons', () => {
    expect(() => monthGrid('2026-01', -1)).toThrow();
    expect(() => monthGrid('2026-01', 1.5)).toThrow();
  });

  it('covers the maximum planning horizon of 60 months', () => {
    const grid = monthGrid('2026-01', 60);
    expect(grid).toHaveLength(60);
    expect(grid[59]).toBe('2030-12');
  });
});

describe('period helpers', () => {
  it('parses and validates YYYY-MM', () => {
    expect(isPeriod('2026-12')).toBe(true);
    expect(isPeriod('2026-13')).toBe(false);
    expect(parsePeriod('2026-03')).toEqual({ year: 2026, month: 3 });
    expect(() => parsePeriod('March 2026')).toThrow();
  });

  it('adds negative offsets', () => {
    expect(addMonths('2026-01', -1)).toBe('2025-12');
    expect(addMonths('2026-01', -13)).toBe('2024-12');
  });

  it('computes signed month distances', () => {
    expect(monthsBetween('2026-01', '2027-01')).toBe(12);
    expect(monthsBetween('2027-01', '2026-11')).toBe(-2);
  });
});

describe('formatPeriod', () => {
  it('formats long and short labels', () => {
    expect(formatPeriod('2026-03')).toBe('Mar 2026');
    expect(formatPeriod('2026-03', 'short')).toBe('Mar 26');
  });

  it('passes unknown strings through unchanged', () => {
    expect(formatPeriod('n/a')).toBe('n/a');
  });
});

describe('byPeriod', () => {
  it('groups rows in grid order and fills gaps', () => {
    const grid = monthGrid('2026-01', 3);
    const rows = [
      { period: '2026-03', key: 'P1-STD' },
      { period: '2026-01', key: 'P1-PRM' },
      { period: '2099-01', key: 'outside-grid' },
    ];
    const grouped = byPeriod(grid, rows);
    expect([...grouped.keys()]).toEqual(grid);
    expect(grouped.get('2026-01')).toHaveLength(1);
    expect(grouped.get('2026-02')).toEqual([]);
    expect(grouped.has('2099-01')).toBe(false);
  });
});
