/**
 * View-model types for the clients feature. Mirror the backend DTOs (`getClient`, `getClientOverview`,
 * `getClientRole`) 1:1 - derived from the generated schema so a contract change surfaces here first.
 * @docs CLI-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type ClientRole = components['schemas']['ClientRole'];

export type PriceBasis = components['schemas']['PriceBasis'];

export interface ClientSummary {
  clientId: string;
  externalRef: string;
  name: string;
  country: string;
  segment: string;
}

export interface ProductGroupIndicators {
  productGroup: ProductGroup;
  corridor: string;
  priceBasis: PriceBasis;
  volume12m: number;
  value12m: number;
  role: ClientRole;
  coverRatio: number;
  openSessions: number;
  sparkline: number[];
}

export interface ClientOverview {
  client: ClientSummary;
  productGroups: ProductGroupIndicators[];
  openSessions: components['schemas']['Session'][];
}

export interface RoleHistoryEntry {
  role: ClientRole;
  source: 'ALGORITHM' | 'MANUAL';
  reason?: string;
  decidedAt: string;
}

export interface ClientRoleInfo {
  productGroup: ProductGroup;
  algorithmRole: ClientRole;
  effectiveRole: ClientRole;
  inboundShare: number;
  history: RoleHistoryEntry[];
}

/** Labels for the two product groups as shown on cards and headers. */
export const PRODUCT_GROUP_LABEL: Record<ProductGroup, string> = {
  product1: 'Product 1 (VLD <-> NRL)',
  product2: 'Product 2 (CST <-> MRD)',
};
