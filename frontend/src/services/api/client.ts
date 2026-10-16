import createClient from 'openapi-fetch';
import type { paths } from '@/services/openapi/schema';
import { getSessionId } from '@/services/api/sessionStore';

/** Header carrying the meeting session id; every `/session/**` endpoint is scoped by it. */
export const SESSION_HEADER = 'X-Harbor-Session';

/**
 * Header params for session-scoped calls. The contract declares `X-Harbor-Session` as required on every
 * `/session/**` operation, so openapi-fetch's types force each such hook to pass
 * `params: { header: sessionHeader(), ... }`; a hook that forgets it fails `npm run typecheck`.
 * Reads the current session from `sessionStore`; hooks are disabled until a session is selected.
 */
export function sessionHeader(): { [SESSION_HEADER]: string } {
  return { [SESSION_HEADER]: getSessionId() ?? '' };
}

/** Typed client generated from `backend/core/src/main/resources/openapi/harbor-api.yaml` (see `npm run generate:api`). */
export const api = createClient<paths>({ baseUrl: '/api/v1' });

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: unknown,
  ) {
    super(`API request failed with status ${status}`);
    this.name = 'ApiError';
  }
}

/** Human-readable text of a failed call: the Problem `detail` (or `title`) sent by the backend, else the status line. */
export function errorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    const problem = err.detail as { detail?: string; title?: string } | undefined;
    return problem?.detail ?? problem?.title ?? err.message;
  }
  return err instanceof Error ? err.message : String(err);
}

interface FetchResult<T> {
  data?: T;
  error?: unknown;
  response: Response;
}

/** Turns an openapi-fetch result into data-or-throw so TanStack Query can track errors. */
export function unwrap<T>(result: FetchResult<T>): T {
  if (result.error !== undefined || result.data === undefined) {
    throw new ApiError(result.response.status, result.error);
  }
  return result.data;
}

/** Variant for endpoints without a response body (204). */
export function ensureOk(result: FetchResult<unknown>): void {
  if (result.error !== undefined || !result.response.ok) {
    throw new ApiError(result.response.status, result.error);
  }
}
