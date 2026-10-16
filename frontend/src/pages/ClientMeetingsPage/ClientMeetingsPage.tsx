import { MeetingsListPage } from '@/pages/shared/components/MeetingsListPage';

/**
 * `/meetings/client` - sessions of kind `CLIENT` (real meetings), with status filter and PDF download for closed ones.
 * @docs SES-001
 */
export function ClientMeetingsPage() {
  return <MeetingsListPage kind="CLIENT" title="Client meetings" />;
}
