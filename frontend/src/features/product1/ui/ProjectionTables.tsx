import { DataTable, type Column } from '@/shared/ui/DataTable';
import { formatQty, formatRatio, formatValue } from '@/shared/utils/format';
import { formatPeriod } from '@/shared/utils/months';
import type { ProjectionRow, ProjectionSummaryRow, ProjectionTables as ProjectionTablesDto, ProjectionTotalRow } from '../product1.types';

export interface ProjectionTablesProps {
  tables: ProjectionTablesDto;
  /** Suffix for monetary columns; omitted while the contract does not provide a price basis. */
  priceBasis?: string;
  /** Column header of the dimension table: "City" (Product 1) or "Transport mode" (Product 2). */
  dimensionLabel: string;
}

function groupedColumns(keyHeader: string, priceBasis?: string): Column<ProjectionRow>[] {
  return [
    { key: 'period', header: 'Month', render: (r) => formatPeriod(r.period) },
    { key: 'key', header: keyHeader },
    { key: 'quantity', header: 'Quantity', align: 'right', render: (r) => formatQty(r.quantity) },
    { key: 'value', header: 'Value', align: 'right', render: (r) => formatValue(r.value, priceBasis) },
    { key: 'landedCost', header: 'Landed cost', align: 'right', render: (r) => formatValue(r.landedCost, priceBasis) },
    { key: 'cumulativeValue', header: 'Cumulative value', align: 'right', render: (r) => formatValue(r.cumulativeValue, priceBasis) },
  ];
}

function summaryColumns(priceBasis?: string): Column<ProjectionSummaryRow>[] {
  return [
    { key: 'period', header: 'Month', render: (r) => formatPeriod(r.period) },
    { key: 'totalQuantity', header: 'Total quantity', align: 'right', render: (r) => formatQty(r.totalQuantity) },
    { key: 'totalValue', header: 'Total value', align: 'right', render: (r) => formatValue(r.totalValue, priceBasis) },
    { key: 'totalLandedCost', header: 'Total landed cost', align: 'right', render: (r) => formatValue(r.totalLandedCost, priceBasis) },
    { key: 'coverRatio', header: 'Cover ratio', align: 'right', render: (r) => formatRatio(r.coverRatio) },
    { key: 'cumulativeValue', header: 'Cumulative value', align: 'right', render: (r) => formatValue(r.cumulativeValue, priceBasis) },
  ];
}

function totalColumns(keyHeader: string, priceBasis?: string): Column<ProjectionTotalRow>[] {
  return [
    { key: 'key', header: keyHeader },
    { key: 'quantity', header: 'Quantity', align: 'right', render: (r) => formatQty(r.quantity) },
    { key: 'value', header: 'Value', align: 'right', render: (r) => formatValue(r.value, priceBasis) },
    { key: 'landedCost', header: 'Landed cost', align: 'right', render: (r) => formatValue(r.landedCost, priceBasis) },
    { key: 'shareOfValue', header: 'Share of value', align: 'right', render: (r) => formatRatio(r.shareOfValue) },
  ];
}

/** Footer of every totals table: the overall line (key `ALL`), identical in all three breakdowns. */
function overallRow(overall: ProjectionTotalRow, priceBasis?: string) {
  const right = { textAlign: 'right' as const };
  return (
    <tr>
      <td>All</td>
      <td style={right}>{formatQty(overall.quantity)}</td>
      <td style={right}>{formatValue(overall.value, priceBasis)}</td>
      <td style={right}>{formatValue(overall.landedCost, priceBasis)}</td>
      <td style={right}>{formatRatio(overall.shareOfValue)}</td>
    </tr>
  );
}

const rowKey = (r: ProjectionRow) => `${r.period}:${r.key}`;
const totalKey = (r: ProjectionTotalRow) => r.key;

/**
 * The four cumulative tables of the monthly projection: by sub-product, by dimension
 * (city / transport mode), by direction (IN / OUT) and the summary with cover ratio; below them the
 * horizon totals (`horizon_totals`): the same three breakdowns summed over the whole horizon, without months,
 * each with the overall line as footer.
 */
export function ProjectionTables({ tables, priceBasis, dimensionLabel }: ProjectionTablesProps) {
  return (
    <div className="projection-tables">
      <section>
        <h3>By sub-product</h3>
        <DataTable dense caption="Projection by sub-product" columns={groupedColumns('Sub-product', priceBasis)} rows={tables.bySubProduct} rowKey={rowKey} />
      </section>
      <section>
        <h3>By {dimensionLabel.toLowerCase()}</h3>
        <DataTable dense caption={`Projection by ${dimensionLabel.toLowerCase()}`} columns={groupedColumns(dimensionLabel, priceBasis)} rows={tables.byDimension} rowKey={rowKey} />
      </section>
      <section>
        <h3>By direction</h3>
        <DataTable dense caption="Projection by direction" columns={groupedColumns('Direction', priceBasis)} rows={tables.byDirection} rowKey={rowKey} />
      </section>
      <section>
        <h3>Summary</h3>
        <DataTable dense caption="Projection summary" columns={summaryColumns(priceBasis)} rows={tables.summary} rowKey={(r) => r.period} />
      </section>
      <section className="projection-totals">
        <h3>Totals over the horizon</h3>
        <div className="totals-grid">
          <DataTable dense caption="Total by sub-product" columns={totalColumns('Sub-product', priceBasis)} rows={tables.totals.bySubProduct} rowKey={totalKey} footer={overallRow(tables.totals.overall, priceBasis)} />
          <DataTable dense caption={`Total by ${dimensionLabel.toLowerCase()}`} columns={totalColumns(dimensionLabel, priceBasis)} rows={tables.totals.byDimension} rowKey={totalKey} footer={overallRow(tables.totals.overall, priceBasis)} />
          <DataTable dense caption="Total by direction" columns={totalColumns('Direction', priceBasis)} rows={tables.totals.byDirection} rowKey={totalKey} footer={overallRow(tables.totals.overall, priceBasis)} />
        </div>
      </section>
    </div>
  );
}
