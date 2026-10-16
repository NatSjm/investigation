import { useDownloadReportPdf } from '@/pages/shared/hook/useDownloadReportPdf';

export interface DownloadPdfButtonProps {
  sessionId: string;
  disabled?: boolean;
  label?: string;
}

/** "Download PDF" button for a closed session (Meetings list, session summary).
 * @docs RPT-001
 */
export function DownloadPdfButton({ sessionId, disabled, label = 'Download PDF' }: DownloadPdfButtonProps) {
  const download = useDownloadReportPdf();
  return (
    <span className="download-pdf">
      <button type="button" disabled={disabled || download.isPending} onClick={() => download.mutate(sessionId)}>
        {download.isPending ? 'Preparing...' : label}
      </button>
      {download.error && (
        <span role="alert" className="error">
          Download failed
        </span>
      )}
    </span>
  );
}
