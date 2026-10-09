/**
 * View-model types for Product 1 (also consumed by `product2`, which shares the projection shape).
 * Mirror `ProductOverview`, `ProjectionTables`, `MovementInput`, `PeerSimulation*` from the contract.
 * @docs P1-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type PriceBasis = components['schemas']['PriceBasis'];

export type Direction = components['schemas']['Direction'];

export type TransportMode = components['schemas']['TransportMode'];

/** Row of the by-sub-product / by-dimension / by-direction tables; `key` is the grouping value. */
export interface ProjectionRow {
  period: string;
  key: string;
  quantity: number;
  value: number;
  landedCost: number;
  cumulativeValue: number;
}

/** Row of the summary table (totals per month + cover ratio). */
export interface ProjectionSummaryRow {
  period: string;
  totalQuantity: number;
  totalValue: number;
  totalLandedCost: number;
  coverRatio: number;
  cumulativeValue: number;
}

/** The four cumulative tables computed by `monthly_projection`. */
export interface ProjectionTables {
  bySubProduct: ProjectionRow[];
  byDimension: ProjectionRow[];
  byDirection: ProjectionRow[];
  summary: ProjectionSummaryRow[];
}

export interface SeriesPoint {
  period: string;
  value: number;
}

/** Cover ratio per month for one sub-product (chart series). */
export interface CoverSeries {
  subProduct: string;
  points: SeriesPoint[];
}

export interface ProductOverview {
  productGroup: ProductGroup;
  priceBasis: PriceBasis;
  horizonMonths: number;
  dimensionValues: string[];
  selectedDimensionValue?: string;
  tables: ProjectionTables;
  coverSeries: CoverSeries[];
}

/** Which breakdown dimension a movement row carries: city (Product 1) or transport mode (Product 2). */
export type MovementDimension = 'city' | 'transportMode';

/** Modelled movement for one month (modal 1). */
export interface MovementInput {
  period: string;
  subProduct: string;
  city?: string;
  transportMode?: TransportMode;
  direction: Direction;
  quantity: number;
  unitPrice: number;
}

/** Peer simulation request (modal 2): similar products at peer firms, scaled. */
export interface PeerSimulationRequest {
  peerSegment: string;
  scalingFactor: number;
}

export interface PeerSimulationResult {
  peerSegment: string;
  scalingFactor: number;
  generatedAt: string;
  series: SeriesPoint[];
}

export const P1_CITIES = ['Aldmoor', 'Brightwater', 'Carrow', 'Dunmere'] as const;

export const P1_SUB_PRODUCTS = ['P1-STD', 'P1-PRM', 'P1-ECO'] as const;
