import { DataTable, type Column } from '@/shared/ui/DataTable';
import { formatDateTime, formatQty } from '@/shared/utils/format';
import { useImportBatches, useTriggerImport } from '../api/useImportBatches';
import type { ImportBatch } from '../admin.types';

const columns: Column<ImportBatch>[] = [
  { key: 'receivedAt', header: 'Received', render: (b) => formatDateTime(b.receivedAt) },
  { key: 'sourceFile', header: 'Source file' },
  { key: 'rowsTotal', header: 'Rows', align: 'right', render: (b) => formatQty(b.rowsTotal) },
  {
    key: 'rowsRejected',
    header: 'Rejected',
    align: 'right',
    render: (b) => <span className={b.rowsRejected > 0 ? 'warn' : undefined}>{formatQty(b.rowsRejected)}</span>,
  },
  { key: 'status', header: 'Status', render: (b) => <span className={`status status-${b.status.toLowerCase()}`}>{b.status}</span> },
];

/** `/admin/imports` - monitor of the daily XLS movement imports with a manual trigger. */
export function ImportsPage() {
  const { data, isLoading, error, dataUpdatedAt } = useImportBatches();
  const trigger = useTriggerImport();
  const running = data?.some((b) => b.status === 'RUNNING') ?? false;

  return (
    <section className="page admin-imports">
      <header className="toolbar">
        <h1>Import batches</h1>
        <div className="actions">
          <button type="button" className="primary" disabled={running || trigger.isPending} onClick={() => trigger.mutate()}>
            {running ? 'Import running...' : 'Run import now'}
          </button>
          {dataUpdatedAt > 0 && <span className="hint">updated {formatDateTime(new Date(dataUpdatedAt).toISOString())}</span>}
        </div>
      </header>
      <p className="hint">Scheduled daily at 02:00; monthly snapshot on the 1st at 03:00.</p>
      {isLoading && <p>Loading batches...</p>}
      {error && <p role="alert">Import batches could not be loaded.</p>}
      {trigger.error && <p role="alert">The import could not be started.</p>}
      <DataTable columns={columns} rows={data ?? []} rowKey={(b) => b.batchId} emptyMessage="No import batches yet" />
    </section>
  );
}
