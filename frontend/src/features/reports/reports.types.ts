/**
 * View-model types for meeting reports. Alias of `Report` from the contract
 * (`reports` module, `ReportController`; table `meeting_report`).
 * @docs RPT-001
 */
import type { components } from '@/api/generated/schema';

/** Report payload stored on session close plus the rendering state of the PDF. */
export type Report = components['schemas']['Report'];

export type ReportStatus = Report['status'];

/** Sections of the payload the preview knows how to render; anything else is shown as raw JSON. */
export const KNOWN_PAYLOAD_SECTIONS = ['client', 'session', 'projectionSummary', 'scenarios', 'stressTest', 'cover'] as const;
