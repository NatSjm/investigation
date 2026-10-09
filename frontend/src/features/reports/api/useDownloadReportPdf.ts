import { useMutation } from '@tanstack/react-query';
import { ApiError, SESSION_HEADER } from '@/api/client';

/**
 * Downloads the rendered PDF (`downloadReportPdf`, `application/pdf`). Uses plain `fetch` because the
 * response is binary; the session header is set explicitly since `/sessions/**` is outside the
 * middleware's `/session/**` scope. Triggers a browser download named `harbor-report-<sessionId>.pdf`.
 * @docs RPT-001
 */
export function useDownloadReportPdf() {
  return useMutation<void, Error, string>({
    mutationFn: async (sessionId) => {
      const response = await fetch(`/api/v1/sessions/${sessionId}/report.pdf`, {
        headers: { Accept: 'application/pdf', [SESSION_HEADER]: sessionId },
      });
      if (!response.ok) throw new ApiError(response.status, await response.text());
      const blob = await response.blob();
      saveBlob(blob, `harbor-report-${sessionId}.pdf`);
    },
  });
}

function saveBlob(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1_000);
}
