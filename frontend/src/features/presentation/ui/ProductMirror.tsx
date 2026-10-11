import { ProjectionTables, CoverRatioChart, P1_CITIES } from '@/features/product1';
import { useProduct1Overview } from '@/features/product1';
import { useProduct2Overview, P2_TRANSPORT_MODES, type TransportMode } from '@/features/product2';
import type { ProductGroup } from '@/api/sessionStore';

export interface ProductMirrorProps {
  productGroup: ProductGroup;
  /** City (Product 1) or transport mode (Product 2) as published by the representative; unknown values mean "all". */
  dimensionValue?: string;
}

const isCity = (v: string | undefined): v is string => v !== undefined && (P1_CITIES as readonly string[]).includes(v);
const isTransportMode = (v: string | undefined): v is TransportMode =>
  v !== undefined && (P2_TRANSPORT_MODES as readonly string[]).includes(v);

/**
 * Read-only mirror of the product overview: the four projection tables and the cover ratio chart for the
 * representative's current filter. No movement / peer simulation modals and no cover quote panel.
 * @docs PRS-001
 */
export function ProductMirror({ productGroup, dimensionValue }: ProductMirrorProps) {
  return productGroup === 'product1' ? (
    <Product1Mirror city={isCity(dimensionValue) ? dimensionValue : undefined} />
  ) : (
    <Product2Mirror transportMode={isTransportMode(dimensionValue) ? dimensionValue : undefined} />
  );
}

function Product1Mirror({ city }: { city?: string }) {
  const { data, isLoading, error } = useProduct1Overview(city);
  if (isLoading) return <p>Computing projection...</p>;
  if (error || !data) return <p role="alert">The projection is not available.</p>;
  return (
    <section className="page product-overview product1">
      <header className="toolbar">
        <h2>Product 1 overview</h2>
        <span className="hint">{city ? `City hub ${city}` : 'All cities'}</span>
      </header>
      <div className="overview-grid">
        <ProjectionTables tables={data.tables} dimensionLabel="City" />
        <aside>
          <CoverRatioChart series={data.coverSeries} />
        </aside>
      </div>
    </section>
  );
}

function Product2Mirror({ transportMode }: { transportMode?: TransportMode }) {
  const { data, isLoading, error } = useProduct2Overview(transportMode);
  if (isLoading) return <p>Computing projection...</p>;
  if (error || !data) return <p role="alert">The projection is not available.</p>;
  return (
    <section className="page product-overview product2">
      <header className="toolbar">
        <h2>Product 2 overview</h2>
        <span className="hint">{transportMode ? `Transport mode ${transportMode}` : 'All modes'}</span>
      </header>
      <div className="overview-grid">
        <ProjectionTables tables={data.tables} dimensionLabel="Transport mode" />
        <aside>
          <CoverRatioChart series={data.coverSeries} />
        </aside>
      </div>
    </section>
  );
}
