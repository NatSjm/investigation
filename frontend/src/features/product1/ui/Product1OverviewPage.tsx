import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { currentPeriod, monthGrid } from '@/shared/utils/months';
import { CoverQuotePanel } from '@/features/cover';
import type { Session } from '@/features/meetings';
import { useProduct1Overview } from '../api/useProduct1Overview';
import { useProduct1Movements } from '../api/useProduct1Movements';
import { usePeerSimulation1 } from '../api/usePeerSimulation1';
import { ProjectionTables } from './ProjectionTables';
import { CoverRatioChart } from './CoverRatioChart';
import { MovementInputModal } from './MovementInputModal';
import { PeerSimulationModal } from './PeerSimulationModal';
import { CitySelector } from './CitySelector';
import { P1_CITIES, P1_SUB_PRODUCTS } from '../product1.types';

const PEER_SEGMENTS = ['Retail', 'Wholesale', 'Manufacturing', 'Distribution'] as const;

/**
 * `/session/:sessionId/product1` - first meeting step for Product 1: city filter, the four
 * projection tables, cover ratio chart, cover quote panel and the two input modals.
 */
export function Product1OverviewPage() {
  const session = useOutletContext<Session>();
  const [city, setCity] = useState<string | undefined>(undefined);
  const [movementsOpen, setMovementsOpen] = useState(false);
  const [peerOpen, setPeerOpen] = useState(false);

  const { data, isLoading, error } = useProduct1Overview(city);
  const movements = useProduct1Movements();
  const peer = usePeerSimulation1();

  if (isLoading) return <p>Computing projection...</p>;
  if (error || !data) return <p role="alert">The Product 1 overview could not be loaded.</p>;

  const periods = monthGrid(currentPeriod(), data.horizonMonths);

  return (
    <section className="page product-overview product1">
      <header className="toolbar">
        <h2>Product 1 overview</h2>
        <CitySelector value={city} options={data.dimensionValues.length ? data.dimensionValues : P1_CITIES} onChange={setCity} />
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
        <ProjectionTables tables={data.tables} priceBasis={data.priceBasis} dimensionLabel="City" />
        <aside>
          <CoverRatioChart series={data.coverSeries} />
          <CoverQuotePanel priceBasis={data.priceBasis} subProducts={P1_SUB_PRODUCTS} />
        </aside>
      </div>

      {movementsOpen && (
        <MovementInputModal
          open={movementsOpen}
          onClose={() => setMovementsOpen(false)}
          periods={periods}
          subProducts={P1_SUB_PRODUCTS}
          dimension="city"
          dimensionValues={P1_CITIES}
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
