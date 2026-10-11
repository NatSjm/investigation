/**
 * View-model types for Product 1 (also consumed by `product2`, which shares the projection shape).
 * Aliases of `ProductOverview`, `Projection`, `ProjectionTables`, `MovementInput`, `PeerSimulation*` from the contract;
 * only `MovementDimension`, `CoverSeries` and the constants are FE-only.
 * @docs P1-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type PriceBasis = components['schemas']['PriceBasis'];

export type Direction = components['schemas']['Direction'];

export type TransportMode = components['schemas']['TransportMode'];

/** Row of the by-sub-product / by-dimension / by-direction tables (`ProjectionLine`); `key` is the grouping value. */
export type ProjectionRow = components['schemas']['ProjectionLine'];

/** Row of the summary table (`SummaryLine`: totals per month + cover ratio). */
export type ProjectionSummaryRow = components['schemas']['SummaryLine'];

/** The four cumulative tables computed by `monthly_projection`. */
export type ProjectionTables = components['schemas']['ProjectionTables'];

/** Projection envelope returned by the movements PUT and the `/projection` GET: tables plus horizon and `computedAt`. */
export type Projection = components['schemas']['Projection'];

export type SeriesPoint = components['schemas']['SparklinePoint'];

/** One cover ratio point: month x sub-product (chart series are flat in the contract). */
export type CoverSeriesPoint = components['schemas']['CoverSeriesPoint'];

/** Cover ratio series of the overview: flat list of `CoverSeriesPoint`, pivoted per sub-product by `CoverRatioChart`. */
export type CoverSeries = CoverSeriesPoint[];

export type ProductOverview = components['schemas']['ProductOverview'];

/** Which breakdown dimension a movement row carries: city (Product 1) or transport mode (Product 2). */
export type MovementDimension = 'city' | 'transportMode';

/** Modelled movement for one month (modal 1). */
export type MovementInput = components['schemas']['MovementInput'];

/** Peer simulation request (modal 2): similar products at peer firms, scaled. */
export type PeerSimulationRequest = components['schemas']['PeerSimulationRequest'];

export type PeerSimulationResult = components['schemas']['PeerSimulationResult'];

export const P1_CITIES = ['Aldmoor', 'Brightwater', 'Carrow', 'Dunmere'] as const;

export const P1_SUB_PRODUCTS = ['P1-STD', 'P1-PRM', 'P1-ECO'] as const;
