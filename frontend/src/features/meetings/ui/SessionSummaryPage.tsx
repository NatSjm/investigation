import { useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { formatDateTime } from '@/shared/utils/format';
import { DownloadPdfButton, ReportPreview, useReport } from '@/features/reports';
import { useCloseSession } from '../api/useCloseSession';
import { RoleOverrideDialog } from './RoleOverrideDialog';
import type { Session } from '../meetings.types';

/**
 * `/session/:sessionId/summary` - last meeting step: role override, close the session,
 * preview the report payload and download the rendered PDF.
 */
export function SessionSummaryPage() {
  const session = useOutletContext<Session>();
  const navigate = useNavigate();
  const [overrideOpen, setOverrideOpen] = useState(false);
  const closeSession = useCloseSession(session.sessionId);
  const { data: report } = useReport(session.sessionId, session.status === 'CLOSED');

  const close = async () => {
    if (!window.confirm('Close this session? The report payload will be stored and rendered.')) return;
    await closeSession.mutateAsync();
    navigate(session.kind === 'PREPARATION' ? '/meetings/preparation' : '/meetings/client');
  };

  return (
    <section className="page session-summary">
      <h2>Summary</h2>
      <dl className="session-facts">
        <dt>Kind</dt>
        <dd>{session.kind === 'CLIENT' ? 'Client meeting' : 'Preparation'}</dd>
        <dt>Started</dt>
        <dd>{formatDateTime(session.startedAt)}</dd>
        <dt>Horizon</dt>
        <dd>{session.horizonMonths} months</dd>
        <dt>Role override</dt>
        <dd>
          {session.roleOverride ? `${session.roleOverride} - ${session.roleOverrideReason ?? ''}` : 'none (algorithm result applies)'}
          {session.status === 'OPEN' && (
            <button type="button" className="link" onClick={() => setOverrideOpen(true)}>
              Change
            </button>
          )}
        </dd>
      </dl>

      {session.status === 'OPEN' ? (
        <div className="actions">
          <button type="button" className="primary" disabled={closeSession.isPending} onClick={close}>
            Close session
          </button>
          {closeSession.error && <p role="alert">The session could not be closed.</p>}
        </div>
      ) : (
        <div className="report">
          <h3>Meeting report</h3>
          {report ? <ReportPreview report={report} /> : <p>Report is being prepared...</p>}
          <DownloadPdfButton sessionId={session.sessionId} disabled={!report?.pdfAvailable} />
        </div>
      )}

      <RoleOverrideDialog
        open={overrideOpen}
        sessionId={session.sessionId}
        currentRole={session.roleOverride}
        onClose={() => setOverrideOpen(false)}
      />
    </section>
  );
}
