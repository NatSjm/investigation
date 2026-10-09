import { DataTable, type Column } from '@/shared/ui/DataTable';
import { formatSignedValue } from '@/shared/utils/format';
import { formatPeriod } from '@/shared/utils/months';
import { DIMENSION_LABEL, type Dimension, type StressRow, type StressScenarioResult } from '../stress.types';

export interface StressTableProps {
  scenario: StressScenarioResult;
  dimension: Dimension;
  priceBasis: string;
}

/**
 * Monthly stress table of one scenario (`stress_test_monthly`): exposure, transport cost delta
 * and cumulative exposure per month and dimension value.
 */
export function StressTable({ scenario, dimension, priceBasis }: StressTableProps) {
  const columns: Column<StressRow>[] = [
    { key: 'period', header: 'Month', render: (r) => formatPeriod(r.period) },
    { key: 'dimensionValue', header: dimension === 'CITY' ? 'City' : 'Transport mode' },
    { key: 'exposure', header: 'Exposure', align: 'right', render: (r) => formatSignedValue(r.exposure, priceBasis) },
    { key: 'transportCostDelta', header: 'Transport cost delta', align: 'right', render: (r) => formatSignedValue(r.transportCostDelta, priceBasis) },
    { key: 'cumulativeExposure', header: 'Cumulative exposure', align: 'right', render: (r) => formatSignedValue(r.cumulativeExposure, priceBasis) },
  ];

  const last = scenario.rows[scenario.rows.length - 1];

  return (
    <section className="stress-table">
      <h3>
        {scenario.scenarioName} <span className="hint">({DIMENSION_LABEL[dimension].toLowerCase()})</span>
      </h3>
      <DataTable
        dense
        caption={`Stress test - ${scenario.scenarioName}`}
        columns={columns}
        rows={scenario.rows}
        rowKey={(r) => `${r.period}:${r.dimensionValue}`}
        emptyMessage="Not computed yet"
        footer={
          last && (
            <tr>
              <th scope="row" colSpan={4}>
                Cumulative exposure at horizon end
              </th>
              <td style={{ textAlign: 'right' }}>{formatSignedValue(last.cumulativeExposure, priceBasis)}</td>
            </tr>
          )
        }
      />
    </section>
  );
}
