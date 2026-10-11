import { MeetingsListPage } from './MeetingsListPage';

/**
 * `/meetings/preparation` - sessions of kind `PREPARATION` (dry runs by the representative), same list and actions.
 * @docs MTG-001
 */
export function PreparationSessionsPage() {
  return <MeetingsListPage kind="PREPARATION" title="Preparation sessions" />;
}
