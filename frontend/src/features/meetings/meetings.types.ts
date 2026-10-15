/**
 * View-model types for meeting sessions. Aliases of `Session`, `CreateSessionRequest`, `SessionCreated` and
 * `RoleOverrideRequest` from the backend contract (`meetings` module, `SessionController`); `SessionFilter` is FE-only.
 * @docs SES-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type ClientRole = components['schemas']['ClientRole'];

export type SessionKind = components['schemas']['SessionKind'];

export type SessionStatus = components['schemas']['SessionStatus'];

export type Session = components['schemas']['Session'];

export type CreateSessionRequest = components['schemas']['CreateSessionRequest'];

export type CreateSessionResponse = components['schemas']['SessionCreated'];

export type RoleOverrideRequest = components['schemas']['RoleOverrideRequest'];

/** Query filter of the Meetings page (`listSessions`). */
export interface SessionFilter {
  clientId?: string;
  status?: SessionStatus;
  kind?: SessionKind;
}
