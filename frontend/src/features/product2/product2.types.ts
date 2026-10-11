/**
 * View-model types for Product 2. The projection shape is identical to Product 1
 * (`ProjectionTables`, `MovementInput`, ...) and is imported from there; only the dimension differs.
 * @docs P2-001
 */
import type { components } from '@/api/generated/schema';
import type { ProductOverview } from '../product1/product1.types';

export type TransportMode = components['schemas']['TransportMode'];

/**
 * Product 2 overview: the contract uses the same `ProductOverview` shape for both product groups;
 * `dimensionFilter` holds the active transport mode (absent = all modes).
 */
export type Product2Overview = ProductOverview;

export const P2_TRANSPORT_MODES: readonly TransportMode[] = ['ROAD', 'RAIL', 'SEA', 'AIR'];

export const P2_SUB_PRODUCTS = ['P2-S', 'P2-M', 'P2-L'] as const;

/** Cities exist for Product 2 as well (overview table only); the primary dimension is the transport mode. */
export const P2_CITIES = ['Aldmoor', 'Brightwater', 'Carrow', 'Dunmere'] as const;

export const TRANSPORT_MODE_LABEL: Record<TransportMode, string> = {
  ROAD: 'Road',
  RAIL: 'Rail',
  SEA: 'Sea',
  AIR: 'Air',
};
