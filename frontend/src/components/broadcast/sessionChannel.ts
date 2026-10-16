/**
 * Cross-window synchronisation between the representative's session window and the client-facing
 * presentation window (`/present/:sessionId`). This is the ONLY module that opens a `BroadcastChannel`;
 * the rest of the app talks through the hooks in `src/components/hook/` (`usePresentationPublisher`,
 * `usePresentationSubscriber`).
 *
 * Channel name: `harbor.session.<sessionId>`. Messages are plain objects (see `PresentationMessage`);
 * the publisher keeps the last message of each type and replays them when a subscriber says `hello`,
 * so a client window opened mid-meeting catches up without the representative navigating again.
 * @docs PRS-001
 */
export const SESSION_CHANNEL_PREFIX = 'harbor.session';

/** `harbor.session.<sessionId>` - one channel per meeting session. */
export function sessionChannelName(sessionId: string): string {
  return `${SESSION_CHANNEL_PREFIX}.${sessionId}`;
}

/** Filters currently selected by the representative; each page publishes only its own slice. */
export interface PresentationView {
  product1?: { city?: string };
  product2?: { transportMode?: string };
  stress?: { dimension: 'CITY' | 'TRANSPORT_MODE' };
}

export type PresentationMessage =
  /** Current sub-page of `/session/:sessionId/*` (full pathname). */
  | { type: 'route'; path: string }
  /** Selected filters of the current page. */
  | ({ type: 'view' } & PresentationView)
  /** The representative closed the session. */
  | { type: 'session-closed' }
  /** Sent by a new subscriber; publishers answer by replaying their last `route` / `view` / `session-closed`. */
  | { type: 'hello' };

export type ReplayableType = Exclude<PresentationMessage['type'], 'hello'>;

/** Messages arrive from another window of the same origin; treat them as data and check the shape. */
export function isPresentationMessage(data: unknown): data is PresentationMessage {
  if (typeof data !== 'object' || data === null) return false;
  const type = (data as { type?: unknown }).type;
  return type === 'route' || type === 'view' || type === 'session-closed' || type === 'hello';
}

/** Opens the session channel; callers close it (`channel.close()`) when their window part unmounts. */
export function openSessionChannel(sessionId: string): BroadcastChannel {
  return new BroadcastChannel(sessionChannelName(sessionId));
}
