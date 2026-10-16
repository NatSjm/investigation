import { formatDateTime } from '@/utils/format';
import { useRegenerateReport } from '@/pages/shared/hook/useReport';
import { KNOWN_PAYLOAD_SECTIONS, type Report } from '@/types/reports';

export interface ReportPreviewProps {
  report: Report;
}

const STATUS_LABEL: Record<Report['status'], string> = {
  PENDING: 'Rendering in progress',
  REQUESTED: 'Rendering requested',
  RENDERED: 'PDF rendered',
  FAILED: 'Rendering failed',
};

/** Read-only view of the report payload grouped by known sections, with a regenerate action.
 * @docs RPT-001
 */
export function ReportPreview({ report }: ReportPreviewProps) {
  const regenerate = useRegenerateReport(report.sessionId);
  const known = KNOWN_PAYLOAD_SECTIONS.filter((k) => k in report.payload);
  const other = Object.keys(report.payload).filter((k) => !(KNOWN_PAYLOAD_SECTIONS as readonly string[]).includes(k));

  return (
    <article className="report-preview">
      <header>
        <span className={`status status-${report.status.toLowerCase()}`}>{STATUS_LABEL[report.status]}</span>
        {report.renderedAt && <span className="hint"> at {formatDateTime(report.renderedAt)}</span>}
        {report.status !== 'PENDING' && (
          <button type="button" className="link" disabled={regenerate.isPending} onClick={() => regenerate.mutate()}>
            Regenerate
          </button>
        )}
      </header>
      {known.map((section) => (
        <details key={section} open={section === 'projectionSummary'}>
          <summary>{section}</summary>
          <pre>{JSON.stringify(report.payload[section], null, 2)}</pre>
        </details>
      ))}
      {other.length > 0 && (
        <details>
          <summary>Other payload sections</summary>
          <pre>{JSON.stringify(Object.fromEntries(other.map((k) => [k, report.payload[k]])), null, 2)}</pre>
        </details>
      )}
      {known.length === 0 && other.length === 0 && <p className="hint">Empty payload.</p>}
    </article>
  );
}
