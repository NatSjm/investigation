import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { currentPeriod, monthGrid } from '@/shared/utils/months';
import { CoverQuotePanel } from '@/features/cover';
import type { Session } from '@/features/meetings';
// Intentional cross-feature import: product2 reuses the product1 tables, chart and modals.
import { ProjectionTables, MovementInputModal, PeerSimulationModal, CoverRatioChart } from '../../product1';
import { useProduct2Overview } from '../api/useProduct2Overview';
import { useProduct2Movements } from '../api/useProduct2Movements';
import { usePeerSimulation2 } from '../api/usePeerSimulation2';
import { TransportModeSelector } from './TransportModeSelector';
import { P2_SUB_PRODUCTS, P2_TRANSPORT_MODES, type TransportMode } from '../product2.types';

const PEER_SEGMENTS = ['Retail', 'Wholesale', 'Manufacturing', 'Distribution'] as const;

/**
 * `/session/:sessionId/product2` - first meeting step for Product 2: transport mode filter,
 * the four projection tables, cover ratio chart, cover quote panel and the two input modals.
 */
export function Product2OverviewPage() {
  const session = useOutletContext<Session>();
  const [mode, setMode] = useState<TransportMode | undefined>(undefined);
  const [movementsOpen, setMovementsOpen] = useState(false);
  const [peerOpen, setPeerOpen] = useState(false);

  const { data, isLoading, error } = useProduct2Overview(mode);
  const movements = useProduct2Movements();
  const peer = usePeerSimulation2();

  if (isLoading) return <p>Computing projection...</p>;
  if (error || !data) return <p role="alert">The Product 2 overview could not be loaded.</p>;

  const periods = monthGrid(currentPeriod(), data.horizonMonths);

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
        <ProjectionTables tables={data.tables} priceBasis={data.priceBasis} dimensionLabel="Transport mode" />
        <aside>
          <CoverRatioChart series={data.coverSeries} />
          <CoverQuotePanel priceBasis={data.priceBasis} subProducts={P2_SUB_PRODUCTS} />
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
        Session {session.sessionId.slice(0, 8)} - horizon {data.horizonMonths} months - price basis {data.priceBasis}
      </p>
    </section>
  );
}
