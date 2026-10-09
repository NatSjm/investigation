/**
 * View-model types for meeting sessions. Mirror `Session`, `CreateSessionRequest` and
 * `RoleOverrideRequest` from the backend contract (`meetings` module, `SessionController`).
 * @docs MTG-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type ClientRole = components['schemas']['ClientRole'];

export type SessionKind = 'CLIENT' | 'PREPARATION';

export type SessionStatus = 'OPEN' | 'CLOSED';

export interface Session {
  sessionId: string;
  clientId: string;
  clientName?: string;
  productGroup: ProductGroup;
  kind: SessionKind;
  status: SessionStatus;
  representativeId: string;
  startedAt: string;
  closedAt?: string;
  roleOverride?: ClientRole;
  roleOverrideReason?: string;
  horizonMonths: number;
  priceBasis: components['schemas']['PriceBasis'];
}

export interface CreateSessionRequest {
  productGroup: ProductGroup;
  kind: SessionKind;
}

export interface CreateSessionResponse {
  sessionId: string;
}

export interface RoleOverrideRequest {
  role: ClientRole;
  reason: string;
}

/** Query filter of the Meetings page (`listSessions`). */
export interface SessionFilter {
  clientId?: string;
  status?: SessionStatus;
  kind?: SessionKind;
}
