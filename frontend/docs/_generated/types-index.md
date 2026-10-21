---
type: Document
title: "Types index (FE)"
description: "Generated map: Types index (FE), derived from src/types/**/*.ts, src/pages/**/*.types.ts, src/pages/**/types.ts; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-21
status: stable
---
# Types index (FE)

> Generated from `src/types/**/*.ts, src/pages/**/*.types.ts, src/pages/**/types.ts` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Exported `interface`/`type` declarations verbatim (types only, ~1 line per field). Mirrors BE DTOs - compare with `api-index.md`.

## `src/types/admin.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type Parameter = components['schemas']['Parameter'];
export type ParameterUpsertRequest = components['schemas']['ParameterUpsert'];
export type ImportBatch = components['schemas']['ImportBatch'];
export type ImportStatus = ImportBatch['status'];
```

## `src/types/clients.ts`
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

## `src/types/cover.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type PriceBasis = components['schemas']['PriceBasis'];
export type CoverSummaryRow = components['schemas']['CoverMonth'];
export type CoverSummary = components['schemas']['CoverSummary'];
export type CoverQuoteRequest = components['schemas']['CoverQuoteRequest'];
export type CoverQuote = components['schemas']['CoverQuote'];
export type CoverPolicy = components['schemas']['CoverPolicy'];
```

## `src/types/market.ts`
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

## `src/types/meetings.ts`
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

## `src/types/presentation.ts`
```ts
export type PresentationStep = 'product1' | 'product2' | 'scenarios' | 'stress-test' | 'waiting';
export interface PresentationState {
  route: string | null;
  view: PresentationView;
  closed: boolean;
}
```

## `src/types/product1.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type PriceBasis = components['schemas']['PriceBasis'];
export type Direction = components['schemas']['Direction'];
export type TransportMode = components['schemas']['TransportMode'];
export type ProjectionRow = components['schemas']['ProjectionLine'];
export type ProjectionSummaryRow = components['schemas']['SummaryLine'];
export type ProjectionTotalRow = components['schemas']['ProjectionTotal'];
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

## `src/types/product2.ts`
```ts
export type TransportMode = components['schemas']['TransportMode'];
export type Product2Overview = ProductOverview;
```

## `src/types/reports.ts`
```ts
export type Report = components['schemas']['Report'];
export type ReportStatus = Report['status'];
```

## `src/types/stress.ts`
```ts
export type ProductGroup = components['schemas']['ProductGroup'];
export type Dimension = components['schemas']['DimensionKind'];
export type StressRow = components['schemas']['StressTestRow'];
export type StressScenarioResult = components['schemas']['StressTestScenarioResult'];
export type StressTestResult = components['schemas']['StressTestResult'];
```

