/**
 * Cross-window synchronisation between the representative's session window and the client-facing
 * presentation window (`/present/:sessionId`). This is the ONLY module that opens a `BroadcastChannel`;
 * the rest of the app talks through `usePresentationPublisher` / `usePresentationSubscriber`.
 *
 * Channel name: `harbor.session.<sessionId>`. Messages are plain objects (see `PresentationMessage`);
 * the publisher keeps the last message of each type and replays them when a subscriber says `hello`,
 * so a client window opened mid-meeting catches up without the representative navigating again.
 * @docs PRS-001
 */
import { useCallback, useEffect, useRef } from 'react';

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

type ReplayableType = Exclude<PresentationMessage['type'], 'hello'>;

/** Messages arrive from another window of the same origin; treat them as data and check the shape. */
function isPresentationMessage(data: unknown): data is PresentationMessage {
  if (typeof data !== 'object' || data === null) return false;
  const type = (data as { type?: unknown }).type;
  return type === 'route' || type === 'view' || type === 'session-closed' || type === 'hello';
}

function openChannel(sessionId: string): BroadcastChannel {
  return new BroadcastChannel(sessionChannelName(sessionId));
}

/**
 * Representative side. Returns `publish(message)`; the channel is opened once per `sessionId`
 * (lazily on first publish or on mount, whichever comes first) and closed on unmount.
 * @docs PRS-001
 */
export function usePresentationPublisher(sessionId: string): (message: PresentationMessage) => void {
  const channelRef = useRef<BroadcastChannel | null>(null);
  const lastRef = useRef<Partial<Record<ReplayableType, PresentationMessage>>>({});

  const open = useCallback((): BroadcastChannel | null => {
    if (!sessionId) return null;
    if (!channelRef.current) {
      const channel = openChannel(sessionId);
      channel.onmessage = (event: MessageEvent<unknown>) => {
        if (!isPresentationMessage(event.data) || event.data.type !== 'hello') return;
        for (const last of Object.values(lastRef.current)) channel.postMessage(last);
      };
      channelRef.current = channel;
    }
    return channelRef.current;
  }, [sessionId]);

  useEffect(() => {
    open();
    return () => {
      channelRef.current?.close();
      channelRef.current = null;
      lastRef.current = {};
    };
  }, [open]);

  return useCallback(
    (message: PresentationMessage) => {
      if (message.type !== 'hello') lastRef.current[message.type] = message;
      open()?.postMessage(message);
    },
    [open],
  );
}

/**
 * Client-screen side. Subscribes to the session channel, announces itself with `hello` and hands every
 * other message to `onMessage` (latest callback is used; no re-subscription on re-render).
 * @docs PRS-001
 */
export function usePresentationSubscriber(sessionId: string, onMessage: (message: PresentationMessage) => void): void {
  const handlerRef = useRef(onMessage);

  useEffect(() => {
    handlerRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    if (!sessionId) return;
    const channel = openChannel(sessionId);
    channel.onmessage = (event: MessageEvent<unknown>) => {
      if (!isPresentationMessage(event.data) || event.data.type === 'hello') return;
      handlerRef.current(event.data);
    };
    channel.postMessage({ type: 'hello' } satisfies PresentationMessage);
    return () => channel.close();
  }, [sessionId]);
}
