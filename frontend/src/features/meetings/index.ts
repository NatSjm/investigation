/**
 * @module meetings — Meeting session lifecycle: create (CLIENT / PREPARATION), list, close, role override, session summary.
 * Meeting session lifecycle: create CLIENT or PREPARATION sessions, list and close them, override the client role, show the session summary.
 * @docs MTG-001
 */
export { MeetingsListPage } from './ui/MeetingsListPage';
export { SessionSummaryPage } from './ui/SessionSummaryPage';
export { RoleOverrideDialog } from './ui/RoleOverrideDialog';
export { useSessions } from './api/useSessions';
export { useSession } from './api/useSessions';
export { useCreateSession } from './api/useCreateSession';
export { useCloseSession } from './api/useCloseSession';
export { useRoleOverride } from './api/useRoleOverride';
export type { Session, SessionKind, SessionStatus, CreateSessionRequest, RoleOverrideRequest, SessionFilter } from './meetings.types';
