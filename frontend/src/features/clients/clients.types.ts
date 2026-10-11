/**
 * View-model types for the clients feature. Aliases of the contract schemas behind `searchClients`, `getClient`,
 * `getClientOverview` and `getClientRole`, so a contract change surfaces here first.
 * @docs CLI-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type ClientRole = components['schemas']['ClientRole'];

export type PriceBasis = components['schemas']['PriceBasis'];

export type ClientSummary = components['schemas']['ClientSummary'];

/** Full client profile (`getClient`): summary plus `createdAt` and role decisions. */
export type Client = components['schemas']['Client'];

export type ProductGroupIndicators = components['schemas']['ProductGroupIndicators'];

export type ClientOverview = components['schemas']['ClientOverview'];

/** One role decision (`RoleDecision`), algorithmic or manual. */
export type RoleHistoryEntry = components['schemas']['RoleDecision'];

export type ClientRoleInfo = components['schemas']['ClientRoleInfo'];

/** Labels for the two product groups as shown on cards and headers. */
export const PRODUCT_GROUP_LABEL: Record<ProductGroup, string> = {
  product1: 'Product 1 (VLD <-> NRL)',
  product2: 'Product 2 (CST <-> MRD)',
};
