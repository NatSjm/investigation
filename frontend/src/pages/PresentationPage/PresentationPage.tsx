import { useCallback, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import type { Session } from '@/types/meetings';
import { defaultDimension } from '@/types/stress';
import { usePresentationSubscriber } from '@/components/hook/usePresentationSubscriber';
import { type PresentationMessage } from '@/components/broadcast/sessionChannel';
import { stepFromPath, type PresentationState } from '@/types/presentation';
import { ProductMirror } from '@/pages/PresentationPage/components/ProductMirror';
import { ScenariosMirror } from '@/pages/PresentationPage/components/ScenariosMirror';
import { StressMirror } from '@/pages/PresentationPage/components/StressMirror';

const initialState: PresentationState = { route: null, view: {}, closed: false };

/**
 * `/present/:sessionId` - what the client sees on the second screen. Follows the representative's
 * `route` and `view` messages and renders the read-only counterpart of the current session step.
 * Shows a waiting panel until the first message arrives or when the current route has no client
 * counterpart (summary, client search), and "Session closed" after `session-closed`.
 * @docs PRS-001
 */
export function PresentationPage() {
  const session = useOutletContext<Session>();
  const [state, setState] = useState<PresentationState>(initialState);

  const onMessage = useCallback((message: PresentationMessage) => {
    setState((prev) => {
      switch (message.type) {
        case 'route':
          return { ...prev, route: message.path };
        case 'view': {
          const { type: _type, ...view } = message;
          return { ...prev, view: { ...prev.view, ...view } };
        }
        case 'session-closed':
          return { ...prev, closed: true };
        default:
          return prev;
      }
    });
  }, []);

  usePresentationSubscriber(session.sessionId, onMessage);

  if (state.closed || session.status === 'CLOSED') {
    return (
      <section className="page presentation-panel" role="status">
        <h2>Session closed</h2>
        <p>Thank you - the meeting report will follow.</p>
      </section>
    );
  }

  switch (stepFromPath(state.route)) {
    case 'product1':
      return <ProductMirror productGroup="product1" dimensionValue={state.view.product1?.city} />;
    case 'product2':
      return <ProductMirror productGroup="product2" dimensionValue={state.view.product2?.transportMode} />;
    case 'scenarios':
      return <ScenariosMirror />;
    case 'stress-test':
      return <StressMirror dimension={state.view.stress?.dimension ?? defaultDimension(session.productGroup)} />;
    default:
      return (
        <section className="page presentation-panel" role="status">
          <h2>Waiting for the representative</h2>
          <p className="hint">The screen follows the meeting as soon as the representative opens a step.</p>
        </section>
      );
  }
}
