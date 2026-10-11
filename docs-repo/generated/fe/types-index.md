---
type: Document
title: "Types index (FE)"
description: "Generated map: Types index (FE), derived from *.types.ts; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-11
status: stable
---
# Types index (FE)

> Generated from `*.types.ts` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Exported `interface`/`type` declarations verbatim (types only, ~1 line per field). Mirrors BE DTOs - compare with `api-index.md`.

## `src/features/admin/admin.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type Parameter = components['schemas']['Parameter'];
export type ParameterUpsertRequest = components['schemas']['ParameterUpsert'];
export type ImportBatch = components['schemas']['ImportBatch'];
export type ImportStatus = ImportBatch['status'];
```

## `src/features/clients/clients.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type ClientRole = components['schemas']['ClientRole'];
export type PriceBasis = components['schemas']['PriceBasis'];
export type ClientSummary = components['schemas']['ClientSummary'];
export type Client = components['schemas']['Client'];
export type ProductGroupIndicators = components['schemas']['ProductGroupIndicators'];
export type ClientOverview = components['schemas']['ClientOverview'];
export type RoleHistoryEntry = components['schemas']['RoleDecision'];
export type ClientRoleInfo = components['schemas']['ClientRoleInfo'];
```

## `src/features/cover/cover.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type PriceBasis = components['schemas']['PriceBasis'];
export type CoverSummaryRow = components['schemas']['CoverMonth'];
export type CoverSummary = components['schemas']['CoverSummary'];
export type CoverQuoteRequest = components['schemas']['CoverQuoteRequest'];
export type CoverQuote = components['schemas']['CoverQuote'];
export type CoverPolicy = components['schemas']['CoverPolicy'];
```

## `src/features/market/market.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type Shock = components['schemas']['Shock'];
export type ScenarioRequest = components['schemas']['ScenarioInput'];
export type ScenarioKind = ScenarioRequest['kind'];
export type Scenario = components['schemas']['Scenario'];
export type BaselinePoint = components['schemas']['BaselinePricePoint'];
export type BaselinePrices = components['schemas']['BaselinePrices'];
export interface ScenarioPathPoint extends BaselinePoint {
  scenarioPrice: number;
  scenarioTransportPrice: number;
}
```

## `src/features/meetings/meetings.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type ClientRole = components['schemas']['ClientRole'];
export type SessionKind = components['schemas']['SessionKind'];
export type SessionStatus = components['schemas']['SessionStatus'];
export type Session = components['schemas']['Session'];
export type CreateSessionRequest = components['schemas']['CreateSessionRequest'];
export type CreateSessionResponse = components['schemas']['SessionCreated'];
export type RoleOverrideRequest = components['schemas']['RoleOverrideRequest'];
export interface SessionFilter {
  clientId?: string;
  status?: SessionStatus;
  kind?: SessionKind;
}
```

## `src/features/presentation/presentation.types.ts`
```ts
export type PresentationStep = 'product1' | 'product2' | 'scenarios' | 'stress-test' | 'waiting';
export interface PresentationState {
  route: string | null;
  view: PresentationView;
  closed: boolean;
}
```

## `src/features/product1/product1.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type PriceBasis = components['schemas']['PriceBasis'];
export type Direction = components['schemas']['Direction'];
export type TransportMode = components['schemas']['TransportMode'];
export type ProjectionRow = components['schemas']['ProjectionLine'];
export type ProjectionSummaryRow = components['schemas']['SummaryLine'];
export type ProjectionTables = components['schemas']['ProjectionTables'];
export type Projection = components['schemas']['Projection'];
export type SeriesPoint = components['schemas']['SparklinePoint'];
export type CoverSeriesPoint = components['schemas']['CoverSeriesPoint'];
export type CoverSeries = CoverSeriesPoint[];
export type ProductOverview = components['schemas']['ProductOverview'];
export type MovementDimension = 'city' | 'transportMode';
export type MovementInput = components['schemas']['MovementInput'];
export type PeerSimulationRequest = components['schemas']['PeerSimulationRequest'];
export type PeerSimulationResult = components['schemas']['PeerSimulationResult'];
```

## `src/features/product2/product2.types.ts`
```ts
export type TransportMode = components['schemas']['TransportMode'];
export type Product2Overview = ProductOverview;
```

## `src/features/reports/reports.types.ts`
```ts
export type Report = components['schemas']['Report'];
export type ReportStatus = Report['status'];
```

## `src/features/stress/stress.types.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type Dimension = components['schemas']['DimensionKind'];
export type StressRow = components['schemas']['StressTestRow'];
export type StressScenarioResult = components['schemas']['StressTestScenarioResult'];
export type StressTestResult = components['schemas']['StressTestResult'];
```

