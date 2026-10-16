import { useEffect, useRef } from 'react';
import { isPresentationMessage, openSessionChannel, type PresentationMessage } from '@/components/broadcast/sessionChannel';

/**
 * Client-screen side of the session channel. Subscribes, announces itself with `hello` and hands every
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
    const channel = openSessionChannel(sessionId);
    channel.onmessage = (event: MessageEvent<unknown>) => {
      if (!isPresentationMessage(event.data) || event.data.type === 'hello') return;
      handlerRef.current(event.data);
    };
    channel.postMessage({ type: 'hello' } satisfies PresentationMessage);
    return () => channel.close();
  }, [sessionId]);
}
