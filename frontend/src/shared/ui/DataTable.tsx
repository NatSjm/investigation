import type { ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: ReactNode;
  /** Cell renderer; defaults to `String(row[key])`. */
  render?: (row: T, index: number) => ReactNode;
  align?: 'left' | 'right' | 'center';
  width?: number | string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T, index: number) => string;
  caption?: string;
  emptyMessage?: string;
  /** Optional footer row (totals). */
  footer?: ReactNode;
  dense?: boolean;
}

/** Plain semantic table used for projection tables, stress rows, parameter lists and import batches. */
export function DataTable<T>({ columns, rows, rowKey, caption, emptyMessage = 'No data', footer, dense }: DataTableProps<T>) {
  return (
    <table className={dense ? 'data-table dense' : 'data-table'}>
      {caption && <caption>{caption}</caption>}
      <thead>
        <tr>
          {columns.map((c) => (
            <th key={c.key} scope="col" style={{ textAlign: c.align ?? 'left', width: c.width }}>
              {c.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 && (
          <tr>
            <td colSpan={columns.length} className="empty">
              {emptyMessage}
            </td>
          </tr>
        )}
        {rows.map((row, i) => (
          <tr key={rowKey(row, i)}>
            {columns.map((c) => (
              <td key={c.key} style={{ textAlign: c.align ?? 'left' }}>
                {c.render ? c.render(row, i) : String((row as Record<string, unknown>)[c.key] ?? '')}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
      {footer && <tfoot>{footer}</tfoot>}
    </table>
  );
}
