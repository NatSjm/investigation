import { useCallback, useEffect, useRef } from 'react';
import {
  isPresentationMessage,
  openSessionChannel,
  type PresentationMessage,
  type ReplayableType,
} from '@/components/broadcast/sessionChannel';

/**
 * Representative side of the session channel. Returns `publish(message)`; the channel is opened once per
 * `sessionId` (lazily on first publish or on mount, whichever comes first) and closed on unmount.
 * Keeps the last message of each type and replays them when a client window says `hello`.
 * @docs PRS-001
 */
export function usePresentationPublisher(sessionId: string): (message: PresentationMessage) => void {
  const channelRef = useRef<BroadcastChannel | null>(null);
  const lastRef = useRef<Partial<Record<ReplayableType, PresentationMessage>>>({});

  const open = useCallback((): BroadcastChannel | null => {
    if (!sessionId) return null;
    if (!channelRef.current) {
      const channel = openSessionChannel(sessionId);
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
