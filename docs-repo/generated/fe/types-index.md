---
type: Document
title: Types index (FE)
description: Generated map: Types index (FE), derived from *.types.ts; read instead of source files.
generated:
  by: process:gen-docs
  at: 2026-10-09
status: stable
---
# Types index (FE)

> Generated from `*.types.ts` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Exported `interface`/`type` declarations verbatim (types only, ~1 line per field). Mirrors BE DTOs - compare with `api-index.md`.

## `src/features/admin/admin.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
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
export interface ImportBatch {
  batchId: string;
  sourceFile: string;
  receivedAt: string;
  rowsTotal: number;
  rowsRejected: number;
  status: ImportStatus;
}
```

## `src/features/clients/clients.types.ts`
```ts
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
```

## `src/features/cover/cover.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type PriceBasis = components['schemas']['PriceBasis'];
export interface CoverSummaryRow {
  period: string;
  subProduct: string;
  coveredValue: number;
  totalValue: number;
  coverRatio: number;
}
export interface CoverSummary {
  priceBasis: PriceBasis;
  rows: CoverSummaryRow[];
}
export interface CoverQuoteRequest {
  subProduct?: string;
  uncoveredValue: number;
  periodFrom: string;
  periodTo: string;
}
export interface CoverQuote {
  quoteId: string;
  uncoveredValue: number;
  premium: number;
  providerRef: string;
  requestedAt: string;
}
export interface CoverPolicy {
  policyId: string;
  productGroup: ProductGroup;
  subProduct: string;
  coveredShare: number;
  premiumRate: number;
  validFrom: string;
  validTo: string;
}
```

## `src/features/market/market.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type ScenarioKind = 'BASE' | 'ADVERSE' | 'CUSTOM';
export interface Shock {
  fromMonth: number;
  priceChangePct: number;
  transportChangePct: number;
}
export interface Scenario {
  scenarioId: string;
  name: string;
  kind: ScenarioKind;
  shocks: Shock[];
  createdBy: string;
  createdAt: string;
}
export interface ScenarioRequest {
  name: string;
  kind: ScenarioKind;
  shocks: Shock[];
}
export interface BaselinePoint {
  period: string;
  price: number;
  transportPrice: number;
}
export interface BaselinePrices {
  productGroup: ProductGroup;
  corridor: string;
  asOf: string;
  points: BaselinePoint[];
}
export interface ScenarioPathPoint extends BaselinePoint {
  scenarioPrice: number;
  scenarioTransportPrice: number;
}
```

## `src/features/meetings/meetings.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type ClientRole = components['schemas']['ClientRole'];
export type SessionKind = 'CLIENT' | 'PREPARATION';
export type SessionStatus = 'OPEN' | 'CLOSED';
export interface Session {
  sessionId: string;
  clientId: string;
  clientName?: string;
  productGroup: ProductGroup;
  kind: SessionKind;
  status: SessionStatus;
  representativeId: string;
  startedAt: string;
  closedAt?: string;
  roleOverride?: ClientRole;
  roleOverrideReason?: string;
  horizonMonths: number;
  priceBasis: components['schemas']['PriceBasis'];
}
export interface CreateSessionRequest {
  productGroup: ProductGroup;
  kind: SessionKind;
}
export interface CreateSessionResponse {
  sessionId: string;
}
export interface RoleOverrideRequest {
  role: ClientRole;
  reason: string;
}
export interface SessionFilter {
  clientId?: string;
  status?: SessionStatus;
  kind?: SessionKind;
}
```

## `src/features/product1/product1.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type PriceBasis = components['schemas']['PriceBasis'];
export type Direction = components['schemas']['Direction'];
export type TransportMode = components['schemas']['TransportMode'];
export interface ProjectionRow {
  period: string;
  key: string;
  quantity: number;
  value: number;
  landedCost: number;
  cumulativeValue: number;
}
export interface ProjectionSummaryRow {
  period: string;
  totalQuantity: number;
  totalValue: number;
  totalLandedCost: number;
  coverRatio: number;
  cumulativeValue: number;
}
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
export type MovementDimension = 'city' | 'transportMode';
export interface MovementInput {
  period: string;
  subProduct: string;
  city?: string;
  transportMode?: TransportMode;
  direction: Direction;
  quantity: number;
  unitPrice: number;
}
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
```

## `src/features/product2/product2.types.ts`
```ts
export type TransportMode = components['schemas']['TransportMode'];
export interface Product2Overview extends ProductOverview {
  productGroup: 'product2';
  selectedDimensionValue?: TransportMode;
}
```

## `src/features/reports/reports.types.ts`
```ts
export type ReportStatus = 'PENDING' | 'RENDERED' | 'FAILED';
export interface Report {
  sessionId: string;
  status: ReportStatus;
  /** Free-form JSON payload (`meeting_report.payload`): projection summary, scenarios, stress results. */
  payload: Record<string, unknown>;
  pdfAvailable: boolean;
  renderedAt?: string;
}
```

## `src/features/stress/stress.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type Dimension = 'CITY' | 'TRANSPORT_MODE';
export interface SeriesPoint {
  period: string;
  value: number;
}
export interface StressRow {
  period: string;
  dimensionValue: string;
  exposure: number;
  transportCostDelta: number;
  cumulativeExposure: number;
}
export interface StressScenarioResult {
  scenarioId: string;
  scenarioName: string;
  rows: StressRow[];
  /** Scenario transport price per month (`scenario_price_path`), drawn in `TransportPriceChart`. */
  transportPricePath: SeriesPoint[];
}
export interface StressTestResult {
  dimension: Dimension;
  computedAt: string;
  scenarios: StressScenarioResult[];
}
```

