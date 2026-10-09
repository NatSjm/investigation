/**
 * View-model types for meeting reports. Mirror `Report` from the contract
 * (`reports` module, `ReportController`; table `meeting_report`).
 * @docs RPT-001
 */

export type ReportStatus = 'PENDING' | 'RENDERED' | 'FAILED';

/** Report payload stored on session close plus the rendering state of the PDF. */
export interface Report {
  sessionId: string;
  status: ReportStatus;
  /** Free-form JSON payload (`meeting_report.payload`): projection summary, scenarios, stress results. */
  payload: Record<string, unknown>;
  pdfAvailable: boolean;
  renderedAt?: string;
}

/** Sections of the payload the preview knows how to render; anything else is shown as raw JSON. */
export const KNOWN_PAYLOAD_SECTIONS = ['client', 'session', 'projectionSummary', 'scenarios', 'stressTest', 'cover'] as const;
