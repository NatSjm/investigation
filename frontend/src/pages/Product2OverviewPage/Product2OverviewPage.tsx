import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { projectionGrid } from '@/utils/months';
import { CoverQuotePanel } from '@/pages/shared/components/CoverQuotePanel';
import type { Session } from '@/types/meetings';
import { usePresentationPublisher } from '@/components/hook/usePresentationPublisher';
import { ProjectionTables } from '@/pages/shared/components/ProjectionTables';
import { MovementInputModal } from '@/pages/shared/components/MovementInputModal';
import { PeerSimulationModal } from '@/pages/shared/components/PeerSimulationModal';
import { CoverRatioChart } from '@/pages/shared/components/CoverRatioChart';
import { useProduct2Overview } from '@/pages/Product2OverviewPage/hook/useProduct2Overview';
import { useProduct2Movements } from '@/pages/Product2OverviewPage/hook/useProduct2Movements';
import { usePeerSimulation2 } from '@/pages/Product2OverviewPage/hook/usePeerSimulation2';
import { TransportModeSelector } from '@/pages/Product2OverviewPage/components/TransportModeSelector';
import { P2_SUB_PRODUCTS, P2_TRANSPORT_MODES, type TransportMode } from '@/types/product2';

const PEER_SEGMENTS = ['Retail', 'Wholesale', 'Manufacturing', 'Distribution'] as const;

/**
 * `/session/:sessionId/product2` - first meeting step for Product 2: transport mode filter,
 * the four projection tables, cover ratio chart, cover quote panel and the two input modals.
 * The horizon comes from the session; the overview itself carries no horizon or price basis.
 * @docs P2-001
 */
export function Product2OverviewPage() {
  const session = useOutletContext<Session>();
  const [mode, setMode] = useState<TransportMode | undefined>(undefined);
  const [movementsOpen, setMovementsOpen] = useState(false);
  const [peerOpen, setPeerOpen] = useState(false);

  const { data, isLoading, error } = useProduct2Overview(mode);
  const movements = useProduct2Movements();
  const peer = usePeerSimulation2();
  const publish = usePresentationPublisher(session.sessionId);

  // Mirror the transport mode filter to the client screen (`view` message).
  useEffect(() => {
    publish({ type: 'view', product2: { transportMode: mode } });
  }, [mode, publish]);

  if (isLoading) return <p>Computing projection...</p>;
  if (error || !data) return <p role="alert">The Product 2 overview could not be loaded.</p>;

  const periods = projectionGrid(session.horizonMonths);

  return (
    <section className="page product-overview product2">
      <header className="toolbar">
        <h2>Product 2 overview</h2>
        <TransportModeSelector value={mode} options={P2_TRANSPORT_MODES} onChange={setMode} />
        <div className="actions">
          <button type="button" onClick={() => setMovementsOpen(true)}>
            Model movements
          </button>
          <button type="button" onClick={() => setPeerOpen(true)}>
            Peer simulation
          </button>
        </div>
      </header>

      <div className="overview-grid">
        <ProjectionTables tables={data.tables} dimensionLabel="Transport mode" />
        <aside>
          <CoverRatioChart series={data.coverSeries} />
          <CoverQuotePanel subProducts={P2_SUB_PRODUCTS} />
        </aside>
      </div>

      {movementsOpen && (
        <MovementInputModal
          open={movementsOpen}
          onClose={() => setMovementsOpen(false)}
          periods={periods}
          subProducts={P2_SUB_PRODUCTS}
          dimension="transportMode"
          dimensionValues={P2_TRANSPORT_MODES}
          pending={movements.isPending}
          onSubmit={(rows) => movements.mutateAsync(rows)}
        />
      )}
      <PeerSimulationModal
        open={peerOpen}
        onClose={() => setPeerOpen(false)}
        segments={PEER_SEGMENTS}
        result={peer.data}
        pending={peer.isPending}
        onSubmit={(req) => peer.mutateAsync(req)}
      />
      <p className="hint">
        Session {session.sessionId.slice(0, 8)} - horizon {session.horizonMonths} months
        {data.role ? ` - role ${data.role}` : ''}
      </p>
    </section>
  );
}
