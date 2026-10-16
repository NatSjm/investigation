import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { projectionGrid } from '@/utils/months';
import { CoverQuotePanel } from '@/pages/shared/components/CoverQuotePanel';
import type { Session } from '@/types/meetings';
import { usePresentationPublisher } from '@/components/hook/usePresentationPublisher';
import { useProduct1Overview } from '@/pages/Product1OverviewPage/hook/useProduct1Overview';
import { useProduct1Movements } from '@/pages/Product1OverviewPage/hook/useProduct1Movements';
import { usePeerSimulation1 } from '@/pages/Product1OverviewPage/hook/usePeerSimulation1';
import { ProjectionTables } from '@/pages/shared/components/ProjectionTables';
import { CoverRatioChart } from '@/pages/shared/components/CoverRatioChart';
import { MovementInputModal } from '@/pages/shared/components/MovementInputModal';
import { PeerSimulationModal } from '@/pages/shared/components/PeerSimulationModal';
import { CitySelector } from '@/pages/Product1OverviewPage/components/CitySelector';
import { P1_CITIES, P1_SUB_PRODUCTS } from '@/types/product1';

const PEER_SEGMENTS = ['Retail', 'Wholesale', 'Manufacturing', 'Distribution'] as const;

/**
 * `/session/:sessionId/product1` - first meeting step for Product 1: city filter, the four
 * projection tables, cover ratio chart, cover quote panel and the two input modals.
 * The horizon comes from the session; the overview itself carries no horizon, price basis or city list.
 * @docs P1-001
 */
export function Product1OverviewPage() {
  const session = useOutletContext<Session>();
  const [city, setCity] = useState<string | undefined>(undefined);
  const [movementsOpen, setMovementsOpen] = useState(false);
  const [peerOpen, setPeerOpen] = useState(false);

  const { data, isLoading, error } = useProduct1Overview(city);
  const movements = useProduct1Movements();
  const peer = usePeerSimulation1();
  const publish = usePresentationPublisher(session.sessionId);

  // Mirror the city filter to the client screen (`view` message).
  useEffect(() => {
    publish({ type: 'view', product1: { city } });
  }, [city, publish]);

  if (isLoading) return <p>Computing projection...</p>;
  if (error || !data) return <p role="alert">The Product 1 overview could not be loaded.</p>;

  const periods = projectionGrid(session.horizonMonths);

  return (
    <section className="page product-overview product1">
      <header className="toolbar">
        <h2>Product 1 overview</h2>
        <CitySelector value={city} options={P1_CITIES} onChange={setCity} />
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
        <ProjectionTables tables={data.tables} dimensionLabel="City" />
        <aside>
          <CoverRatioChart series={data.coverSeries} />
          <CoverQuotePanel subProducts={P1_SUB_PRODUCTS} />
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
        Session {session.sessionId.slice(0, 8)} - horizon {session.horizonMonths} months
        {data.role ? ` - role ${data.role}` : ''}
      </p>
    </section>
  );
}
