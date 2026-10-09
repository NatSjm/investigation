/**
 * View-model types for administration. Mirror `Parameter` and `ImportBatch` from the contract
 * (`admin` module, `AdminController`; tables `parameter_set`, `import_batch`).
 * @docs ADM-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

/** One row of `parameter_set`; the scope columns narrow a key to a product group, country or dimension value. */
export interface Parameter {
  key: string;
  scopeProductGroup?: ProductGroup;
  scopeCountry?: string;
  scopeValue?: string;
  value: number;
  validFrom: string;
  updatedBy: string;
  updatedAt: string;
}

export interface ParameterUpsertRequest {
  value: number;
  scopeProductGroup?: ProductGroup;
  scopeCountry?: string;
  scopeValue?: string;
  validFrom: string;
}

export type ImportStatus = 'RUNNING' | 'DONE' | 'FAILED';

/** One daily XLS import run (`import_batch`). */
export interface ImportBatch {
  batchId: string;
  sourceFile: string;
  receivedAt: string;
  rowsTotal: number;
  rowsRejected: number;
  status: ImportStatus;
}

/** Known parameter keys (see blueprint 3.4); unknown keys are still rendered. */
export const PARAMETER_KEYS = [
  'role.min_volume',
  'role.importer_threshold',
  'role.exporter_threshold',
  'tariff.rate',
  'handling.cost',
  'transport.cost',
  'cover.default_premium_rate',
  'projection.horizon_months_default',
  'stress.rounding_scale',
  'peer.scaling_default',
] as const;
