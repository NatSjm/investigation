import createClient, { type Middleware } from 'openapi-fetch';
import type { paths } from './generated/schema';
import { getSessionId } from './sessionStore';

/** Header carrying the meeting session id; every `/session/**` endpoint is scoped by it. */
export const SESSION_HEADER = 'X-Harbor-Session';

/**
 * Adds `X-Harbor-Session` to session-scoped requests (`/session/**`).
 * Client-level endpoints (`/clients`, `/sessions`, `/admin`) are left untouched.
 */
const sessionHeaderMiddleware: Middleware = {
  onRequest({ request }) {
    if (request.url.includes('/session/')) {
      const sessionId = getSessionId();
      if (sessionId) request.headers.set(SESSION_HEADER, sessionId);
    }
    return request;
  },
};

/** Typed client generated from `backend/core/src/main/resources/openapi/harbor-api.yaml` (see `npm run generate:api`). */
export const api = createClient<paths>({ baseUrl: '/api/v1' });
api.use(sessionHeaderMiddleware);

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: unknown,
  ) {
    super(`API request failed with status ${status}`);
    this.name = 'ApiError';
  }
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
