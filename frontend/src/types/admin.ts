/**
 * View-model types for administration. Aliases of `Parameter`, `ParameterUpsert` and `ImportBatch` from the contract
 * (`admin` module, `AdminController`; tables `parameter_set`, `import_batch`).
 * @docs ADM-001
 */
import type { components } from '@/services/openapi/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

/** One row of `parameter_set`; the scope columns narrow a key to a product group, country or dimension value. */
export type Parameter = components['schemas']['Parameter'];

export type ParameterUpsertRequest = components['schemas']['ParameterUpsert'];

/** One daily XLS import run (`import_batch`). */
export type ImportBatch = components['schemas']['ImportBatch'];

export type ImportStatus = ImportBatch['status'];

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
