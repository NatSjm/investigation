import { MeetingsListPage } from '@/pages/shared/components/MeetingsListPage';

/**
 * `/meetings/preparation` - sessions of kind `PREPARATION` (dry runs by the representative), same list and actions.
 * @docs SES-001
 */
export function PreparationSessionsPage() {
  return <MeetingsListPage kind="PREPARATION" title="Preparation sessions" />;
}
