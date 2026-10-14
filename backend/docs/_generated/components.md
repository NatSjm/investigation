---
type: Document
title: "Components (BE)"
description: "One row per class: layer, stereotype, injected dependencies, tables, @docs tags and file:line; business context = class-name prefix."
generated:
  by: process:gen-docs
  at: 2026-10-14
status: stable
---
# Components (BE)

> Generated from `top-level Kotlin declarations per layer` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
154 declaration(s). Per layer: (root) 4, advice 1, api 9, client 5, component 7, config 4, context 3, dao 17, databind 2, enums 15, event 9, events 5, exception 6, job 2, manager 10, mapper 9, model 19, service 15, utils 8, validator 4. Business context of a class = its name prefix (docs repo `contexts.yml`).

| Class | Layer | Module | Kind | Depends on | Tables | @docs | Location |
|---|---|---|---|---|---|---|---|
| `HarborApplication` | (root) | core | SpringBootApplication |  |  |  | `core/src/main/kotlin/harbor/HarborApplication.kt:13` |
| `HarborKafkaClient` | (root) | kafka_client | object |  |  |  | `kafka_client/src/main/kotlin/harbor/kafka/HarborKafkaClient.kt:22` |
| `JsonSerde` | (root) | kafka_client | class |  |  |  | `kafka_client/src/main/kotlin/harbor/kafka/JsonSerde.kt:16` |
| `Topics` | (root) | kafka_client | object |  |  |  | `kafka_client/src/main/kotlin/harbor/kafka/Topics.kt:8` |
| `GlobalExceptionAdvice` | advice | core | RestControllerAdvice |  |  |  | `core/src/main/kotlin/harbor/advice/GlobalExceptionAdvice.kt:32` |
| `AdminController` | api | core | RestController | `AdminManager` |  |  | `core/src/main/kotlin/harbor/api/AdminController.kt:17` |
| `ClientController` | api | core | RestController | `ClientManager` |  |  | `core/src/main/kotlin/harbor/api/ClientController.kt:20` |
| `CoverController` | api | core | RestController | `CoverManager` |  |  | `core/src/main/kotlin/harbor/api/CoverController.kt:20` |
| `Product1Controller` | api | core | RestController | `Product1Manager` |  |  | `core/src/main/kotlin/harbor/api/Product1Controller.kt:21` |
| `Product2Controller` | api | core | RestController | `Product2Manager` |  |  | `core/src/main/kotlin/harbor/api/Product2Controller.kt:22` |
| `ReportController` | api | core | RestController | `ReportManager` |  |  | `core/src/main/kotlin/harbor/api/ReportController.kt:21` |
| `ScenarioController` | api | core | RestController | `MarketManager` |  |  | `core/src/main/kotlin/harbor/api/ScenarioController.kt:20` |
| `SessionController` | api | core | RestController | `MeetingManager` |  |  | `core/src/main/kotlin/harbor/api/SessionController.kt:22` |
| `StressTestController` | api | core | RestController | `StressManager` |  |  | `core/src/main/kotlin/harbor/api/StressTestController.kt:18` |
| `ClientRegistryClient` | client | core | Component |  |  |  | `core/src/main/kotlin/harbor/client/ClientRegistryClient.kt:16` |
| `CoverProviderClient` | client | core | Component |  |  |  | `core/src/main/kotlin/harbor/client/CoverProviderClient.kt:19` |
| `DocumentServiceClient` | client | core | Component |  |  |  | `core/src/main/kotlin/harbor/client/DocumentServiceClient.kt:17` |
| `FileExchangeClient` | client | core | Component |  |  |  | `core/src/main/kotlin/harbor/client/FileExchangeClient.kt:17` |
| `MarketDataClient` | client | core | Component |  |  |  | `core/src/main/kotlin/harbor/client/MarketDataClient.kt:19` |
| `ReportTemplateLoader` | component | core | Component |  |  |  | `core/src/main/kotlin/harbor/component/ReportTemplateLoader.kt:15` |
| `SessionHeaderFilter` | component | core | Component | `MeetingSessionDao`, `SessionScopeService` |  |  | `core/src/main/kotlin/harbor/component/SessionHeaderFilter.kt:31` |
| `WorkbookDelimitedReader` | component | core | class |  |  |  | `core/src/main/kotlin/harbor/component/WorkbookDelimitedReader.kt:7` |
| `WorkbookReader` | component | core | interface |  |  |  | `core/src/main/kotlin/harbor/component/WorkbookReader.kt:9` |
| `WorkbookReaderFactory` | component | core | Component | `XlsWorkbookOpener` |  |  | `core/src/main/kotlin/harbor/component/WorkbookReaderFactory.kt:11` |
| `XlsMovementParser` | component | core | Component |  |  |  | `core/src/main/kotlin/harbor/component/XlsMovementParser.kt:32` |
| `XlsWorkbookOpener` | component | core | interface |  |  |  | `core/src/main/kotlin/harbor/component/XlsWorkbookOpener.kt:8` |
| `JacksonConfig` | config | core | Configuration |  |  |  | `core/src/main/kotlin/harbor/config/JacksonConfig.kt:17` |
| `KafkaConfig` | config | core | Configuration |  |  |  | `core/src/main/kotlin/harbor/config/KafkaConfig.kt:25` |
| `SchedulingConfig` | config | core | Configuration |  |  |  | `core/src/main/kotlin/harbor/config/SchedulingConfig.kt:12` |
| `WebConfig` | config | core | Configuration |  |  |  | `core/src/main/kotlin/harbor/config/WebConfig.kt:17` |
| `CurrentUser` | context | core | interface |  |  |  | `core/src/main/kotlin/harbor/context/CurrentUser.kt:7` |
| `SessionContext` | context | core | object |  |  |  | `core/src/main/kotlin/harbor/context/SessionContext.kt:12` |
| `SessionScope` | context | core | class | `ProductGroup`, `SessionKind`, `PriceBasis`, `ClientRole` |  |  | `core/src/main/kotlin/harbor/context/SessionScope.kt:13` |
| `BaselinePriceDao` | dao | core | Repository |  | `baseline_price` |  | `core/src/main/kotlin/harbor/dao/BaselinePriceDao.kt:10` |
| `ClientProfileDao` | dao | core | Repository |  | `client_profile` |  | `core/src/main/kotlin/harbor/dao/ClientProfileDao.kt:10` |
| `ClientRoleDao` | dao | core | Repository |  | `client_role` |  | `core/src/main/kotlin/harbor/dao/ClientRoleDao.kt:10` |
| `CoverPolicyDao` | dao | core | Repository |  | `cover_policy` |  | `core/src/main/kotlin/harbor/dao/CoverPolicyDao.kt:10` |
| `CoverQuoteDao` | dao | core | Repository |  | `cover_quote` |  | `core/src/main/kotlin/harbor/dao/CoverQuoteDao.kt:9` |
| `GoodsMovementDao` | dao | core | Repository |  | `movement_monthly`, `goods_movement` |  | `core/src/main/kotlin/harbor/dao/GoodsMovementDao.kt:12` |
| `ImportBatchDao` | dao | core | Repository |  | `import_batch` |  | `core/src/main/kotlin/harbor/dao/ImportBatchDao.kt:9` |
| `MarketScenarioDao` | dao | core | Repository |  | `market_scenario` |  | `core/src/main/kotlin/harbor/dao/MarketScenarioDao.kt:9` |
| `MeetingReportDao` | dao | core | Repository |  | `meeting_report` |  | `core/src/main/kotlin/harbor/dao/MeetingReportDao.kt:9` |
| `MeetingSessionDao` | dao | core | Repository |  | `meeting_session` |  | `core/src/main/kotlin/harbor/dao/MeetingSessionDao.kt:13` |
| `MovementMonthlyDao` | dao | core | Repository |  | `movement_monthly` |  | `core/src/main/kotlin/harbor/dao/MovementMonthlyDao.kt:13` |
| `ParameterDao` | dao | core | Repository |  | `parameter_set` |  | `core/src/main/kotlin/harbor/dao/ParameterDao.kt:12` |
| `ProjectionDao` | dao | core | Repository |  | `projection_by_subproduct`, `projection_by_dimension`, `projection_by_direction`, `projection_summary` |  | `core/src/main/kotlin/harbor/dao/ProjectionDao.kt:23` |
| `SessionClientConfigDao` | dao | core | Repository |  | `session_client_config` |  | `core/src/main/kotlin/harbor/dao/SessionClientConfigDao.kt:9` |
| `SessionMovementInputDao` | dao | core | Repository |  | `session_movement_input` |  | `core/src/main/kotlin/harbor/dao/SessionMovementInputDao.kt:10` |
| `SessionPeerSimulationDao` | dao | core | Repository |  | `session_peer_simulation` |  | `core/src/main/kotlin/harbor/dao/SessionPeerSimulationDao.kt:9` |
| `StressTestResultDao` | dao | core | Repository |  | `stress_test_result` |  | `core/src/main/kotlin/harbor/dao/StressTestResultDao.kt:10` |
| `MoneySerializer` | databind | core | class |  |  |  | `core/src/main/kotlin/harbor/databind/MoneySerializer.kt:12` |
| `PeriodDeserializer` | databind | core | class |  |  |  | `core/src/main/kotlin/harbor/databind/PeriodDeserializer.kt:14` |
| `ClientRole` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/ClientRole.kt:4` |
| `CoverPreference` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/CoverPreference.kt:4` |
| `DimensionKind` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/DimensionKind.kt:4` |
| `Direction` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/Direction.kt:4` |
| `ImportStatus` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/ImportStatus.kt:4` |
| `ParameterKey` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:4` |
| `PriceBasis` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/PriceBasis.kt:4` |
| `ProductGroup` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/ProductGroup.kt:7` |
| `ReportStatus` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/ReportStatus.kt:4` |
| `RoleSource` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/RoleSource.kt:4` |
| `ScenarioKind` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/ScenarioKind.kt:4` |
| `SessionKind` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/SessionKind.kt:4` |
| `SessionStatus` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/SessionStatus.kt:4` |
| `StressDimension` | enums | core | class | `DimensionKind` |  |  | `core/src/main/kotlin/harbor/enums/StressDimension.kt:7` |
| `TransportMode` | enums | core | class |  |  |  | `core/src/main/kotlin/harbor/enums/TransportMode.kt:4` |
| `ClientRoleSessionClosedListener` | event | core | Component, KafkaListener | `ClientRoleService` |  |  | `core/src/main/kotlin/harbor/event/ClientRoleSessionClosedListener.kt:18` |
| `MarketPricesListener` | event | core | Component, KafkaListener | `BaselinePriceService` |  |  | `core/src/main/kotlin/harbor/event/MarketPricesListener.kt:18` |
| `MovementsLoadedPublisher` | event | core | Component, KafkaProducer | `GoodsMovementDao` |  |  | `core/src/main/kotlin/harbor/event/MovementsLoadedPublisher.kt:15` |
| `Product1ProjectionRefreshListener` | event | core | Component, KafkaListener | `SessionScopeService`, `ProjectionService` |  |  | `core/src/main/kotlin/harbor/event/Product1ProjectionRefreshListener.kt:17` |
| `Product2ProjectionRefreshListener` | event | core | Component, KafkaListener | `SessionScopeService`, `ProjectionService` |  |  | `core/src/main/kotlin/harbor/event/Product2ProjectionRefreshListener.kt:17` |
| `ReportRenderedListener` | event | core | Component, KafkaListener | `ReportManager` |  |  | `core/src/main/kotlin/harbor/event/ReportRenderedListener.kt:10` |
| `ReportRenderRequester` | event | core | Component, KafkaProducer | `ReportTemplateLoader` |  |  | `core/src/main/kotlin/harbor/event/ReportRenderRequester.kt:16` |
| `ReportSessionClosedListener` | event | core | Component, KafkaListener | `ReportManager` |  |  | `core/src/main/kotlin/harbor/event/ReportSessionClosedListener.kt:14` |
| `SessionEventsPublisher` | event | core | Component, KafkaProducer |  |  |  | `core/src/main/kotlin/harbor/event/SessionEventsPublisher.kt:14` |
| `MovementsLoadedEvent` | events | kafka_client | class |  |  |  | `kafka_client/src/main/kotlin/harbor/kafka/events/MovementsLoadedEvent.kt:10` |
| `PricesUpdatedEvent` | events | kafka_client | class |  |  |  | `kafka_client/src/main/kotlin/harbor/kafka/events/PricesUpdatedEvent.kt:11` |
| `ReportRendered` | events | kafka_client | class |  |  |  | `kafka_client/src/main/kotlin/harbor/kafka/events/ReportRendered.kt:6` |
| `ReportRenderRequested` | events | kafka_client | class |  |  |  | `kafka_client/src/main/kotlin/harbor/kafka/events/ReportRenderRequested.kt:11` |
| `SessionClosedEvent` | events | kafka_client | class |  |  |  | `kafka_client/src/main/kotlin/harbor/kafka/events/SessionClosedEvent.kt:12` |
| `MissingParameterException` | exception | core | class |  |  |  | `core/src/main/kotlin/harbor/exception/MissingParameterException.kt:6` |
| `NotFoundException` | exception | core | class |  |  |  | `core/src/main/kotlin/harbor/exception/NotFoundException.kt:4` |
| `SessionClosedException` | exception | core | class |  |  |  | `core/src/main/kotlin/harbor/exception/SessionClosedException.kt:6` |
| `SessionHeaderMissingException` | exception | core | class |  |  |  | `core/src/main/kotlin/harbor/exception/SessionHeaderMissingException.kt:4` |
| `SessionNotBoundException` | exception | core | class |  |  |  | `core/src/main/kotlin/harbor/exception/SessionNotBoundException.kt:4` |
| `ValidationException` | exception | core | class |  |  |  | `core/src/main/kotlin/harbor/exception/ValidationException.kt:4` |
| `DailyMovementImportJob` | job | core | Component, Scheduled | `ImportManager` | `goods_movement` |  | `core/src/main/kotlin/harbor/job/DailyMovementImportJob.kt:12` |
| `MonthlySnapshotJob` | job | core | Component, Scheduled | `ImportManager` |  |  | `core/src/main/kotlin/harbor/job/MonthlySnapshotJob.kt:14` |
| `AdminManager` | manager | core | Service | `ParameterService`, `ParameterValidator`, `MovementImportService`, `CurrentUser` |  | `ADM-001` | `core/src/main/kotlin/harbor/manager/AdminManager.kt:24` |
| `ClientManager` | manager | core | Service | `ClientProfileService`, `ClientRoleDao`, `ClientRoleService`, `ClientOverviewService` |  | `CLI-001` | `core/src/main/kotlin/harbor/manager/ClientManager.kt:25` |
| `CoverManager` | manager | core | Service | `CoverPolicyDao`, `ProjectionService`, `CoverRatioService`, `CoverQuoteService`, `ClientProfileService` |  | `COV-001` | `core/src/main/kotlin/harbor/manager/CoverManager.kt:25` |
| `ImportManager` | manager | core | Service | `MovementImportService` |  | `IMP-001` | `core/src/main/kotlin/harbor/manager/ImportManager.kt:18` |
| `MarketManager` | manager | core | Service | `ScenarioService`, `BaselinePriceService` |  | `MKT-001` | `core/src/main/kotlin/harbor/manager/MarketManager.kt:21` |
| `MeetingManager` | manager | core | Service | `MeetingSessionDao`, `SessionClientConfigDao`, `ClientProfileService`, `ParameterService`, `RoleOverrideValidator`, `SessionEventsPublisher`, `CurrentUser` |  | `MTG-001` | `core/src/main/kotlin/harbor/manager/MeetingManager.kt:37` |
| `Product1Manager` | manager | core | Service | `ProjectionService`, `ProjectionInputAssembler`, `PeerSimulationService`, `ClientRoleService`, `MovementInputValidator` |  | `P1-001` | `core/src/main/kotlin/harbor/manager/Product1Manager.kt:26` |
| `Product2Manager` | manager | core | Service | `ProjectionService`, `ProjectionInputAssembler`, `PeerSimulationService`, `ClientRoleService`, `MovementInputValidator` |  | `P2-001` | `core/src/main/kotlin/harbor/manager/Product2Manager.kt:26` |
| `ReportManager` | manager | core | Service | `MeetingReportDao`, `MeetingSessionDao`, `ReportPayloadService`, `ReportRenderRequester`, `DocumentServiceClient` |  | `RPT-001` | `core/src/main/kotlin/harbor/manager/ReportManager.kt:26` |
| `StressManager` | manager | core | Service | `StressTestService`, `StressTestResultDao`, `MarketScenarioDao`, `ClientRoleService` |  | `STR-001` | `core/src/main/kotlin/harbor/manager/StressManager.kt:30` |
| `ClientMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/ClientMapper.kt:21` |
| `CoverMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/CoverMapper.kt:18` |
| `ImportBatchMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/ImportBatchMapper.kt:8` |
| `ParameterMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/ParameterMapper.kt:12` |
| `ProjectionMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/ProjectionMapper.kt:31` |
| `ReportMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/ReportMapper.kt:9` |
| `ScenarioMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/ScenarioMapper.kt:18` |
| `SessionMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/SessionMapper.kt:17` |
| `StressMapper` | mapper | core | object |  |  |  | `core/src/main/kotlin/harbor/mapper/StressMapper.kt:14` |
| `BaselinePrice` | model | core | Entity | `ProductGroup` | `baseline_price` |  | `core/src/main/kotlin/harbor/model/BaselinePrice.kt:20` |
| `ClientOverviewIndicators` | model | core | class | `ProductGroup`, `ClientRole` |  |  | `core/src/main/kotlin/harbor/model/ClientOverviewIndicators.kt:13` |
| `ClientProfile` | model | core | Entity |  | `client_profile` |  | `core/src/main/kotlin/harbor/model/ClientProfile.kt:14` |
| `ClientRoleDecision` | model | core | Entity | `ProductGroup`, `ClientRole`, `RoleSource` | `client_role` |  | `core/src/main/kotlin/harbor/model/ClientRoleDecision.kt:22` |
| `CoverPolicy` | model | core | Entity | `ProductGroup` | `cover_policy` |  | `core/src/main/kotlin/harbor/model/CoverPolicy.kt:21` |
| `CoverQuote` | model | core | Entity |  | `cover_quote` |  | `core/src/main/kotlin/harbor/model/CoverQuote.kt:12` |
| `GoodsMovement` | model | core | Entity | `ProductGroup`, `TransportMode`, `Direction`, `PriceBasis` | `goods_movement` |  | `core/src/main/kotlin/harbor/model/GoodsMovement.kt:23` |
| `ImportBatch` | model | core | Entity | `ImportStatus` | `import_batch` |  | `core/src/main/kotlin/harbor/model/ImportBatch.kt:14` |
| `MarketScenario` | model | core | Entity | `ScenarioKind` | `market_scenario` |  | `core/src/main/kotlin/harbor/model/MarketScenario.kt:20` |
| `MeetingReport` | model | core | Entity | `ReportStatus` | `meeting_report` |  | `core/src/main/kotlin/harbor/model/MeetingReport.kt:19` |
| `MeetingSession` | model | core | Entity | `ProductGroup`, `SessionKind`, `SessionStatus`, `ClientRole` | `meeting_session` |  | `core/src/main/kotlin/harbor/model/MeetingSession.kt:25` |
| `MovementMonthly` | model | core | Entity | `ProductGroup`, `TransportMode`, `Direction` | `movement_monthly` |  | `core/src/main/kotlin/harbor/model/MovementMonthly.kt:22` |
| `Parameter` | model | core | Entity | `ProductGroup` | `parameter_set` |  | `core/src/main/kotlin/harbor/model/Parameter.kt:20` |
| `ProjectionRow` | model | core | class |  |  |  | `core/src/main/kotlin/harbor/model/ProjectionRow.kt:11` |
| `ScenarioShock` | model | core | class |  |  |  | `core/src/main/kotlin/harbor/model/ScenarioShock.kt:7` |
| `SessionClientConfig` | model | core | Entity | `PriceBasis`, `CoverPreference` | `session_client_config` |  | `core/src/main/kotlin/harbor/model/SessionClientConfig.kt:17` |
| `SessionMovementInput` | model | core | Entity | `TransportMode`, `Direction` | `session_movement_input` |  | `core/src/main/kotlin/harbor/model/SessionMovementInput.kt:20` |
| `SessionPeerSimulation` | model | core | Entity |  | `session_peer_simulation` |  | `core/src/main/kotlin/harbor/model/SessionPeerSimulation.kt:15` |
| `StressTestResult` | model | core | Entity |  | `stress_test_result` |  | `core/src/main/kotlin/harbor/model/StressTestResult.kt:17` |
| `BaselinePriceService` | service | core | Service | `BaselinePriceDao`, `MarketDataClient` |  |  | `core/src/main/kotlin/harbor/service/BaselinePriceService.kt:23` |
| `ClientOverviewService` | service | core | Service | `MovementMonthlyDao`, `MeetingSessionDao`, `ClientRoleService`, `CoverRatioService` |  |  | `core/src/main/kotlin/harbor/service/ClientOverviewService.kt:23` |
| `ClientProfileService` | service | core | Service | `ClientProfileDao`, `ClientRegistryClient` |  |  | `core/src/main/kotlin/harbor/service/ClientProfileService.kt:16` |
| `ClientRoleService` | service | core | Service | `ClientRoleDao`, `MovementMonthlyDao`, `ParameterService` |  |  | `core/src/main/kotlin/harbor/service/ClientRoleService.kt:28` |
| `CoverQuoteService` | service | core | Service | `CoverQuoteDao`, `CoverProviderClient`, `ParameterService` |  |  | `core/src/main/kotlin/harbor/service/CoverQuoteService.kt:23` |
| `CoverRatioService` | service | core | Service | `CoverPolicyDao`, `MovementMonthlyDao` |  |  | `core/src/main/kotlin/harbor/service/CoverRatioService.kt:26` |
| `MovementImportService` | service | core | Service | `ImportBatchDao`, `GoodsMovementDao`, `MovementMonthlyDao`, `FileExchangeClient`, `WorkbookReaderFactory`, `XlsMovementParser`, `MovementsLoadedPublisher`, `ClientProfileService` |  |  | `core/src/main/kotlin/harbor/service/MovementImportService.kt:31` |
| `ParameterService` | service | core | Service | `ParameterDao` |  |  | `core/src/main/kotlin/harbor/service/ParameterService.kt:23` |
| `PeerSimulationService` | service | core | Service | `MovementMonthlyDao`, `SessionPeerSimulationDao`, `ParameterService` |  |  | `core/src/main/kotlin/harbor/service/PeerSimulationService.kt:24` |
| `ProjectionInputAssembler` | service | core | Component | `MovementMonthlyDao`, `SessionMovementInputDao`, `ParameterService`, `BaselinePriceService` |  |  | `core/src/main/kotlin/harbor/service/ProjectionInputAssembler.kt:30` |
| `ProjectionService` | service | core | Service | `ProjectionInputAssembler`, `ProjectionDao`, `SessionMovementInputDao`, `CoverRatioService` |  |  | `core/src/main/kotlin/harbor/service/ProjectionService.kt:27` |
| `ReportPayloadService` | service | core | Service | `MeetingSessionDao`, `SessionClientConfigDao`, `ClientProfileService`, `ProjectionDao`, `MarketScenarioDao`, `StressTestResultDao` |  |  | `core/src/main/kotlin/harbor/service/ReportPayloadService.kt:22` |
| `ScenarioService` | service | core | Service | `MarketScenarioDao`, `ScenarioValidator` |  |  | `core/src/main/kotlin/harbor/service/ScenarioService.kt:20` |
| `SessionScopeService` | service | core | Service | `MeetingSessionDao`, `SessionClientConfigDao` |  |  | `core/src/main/kotlin/harbor/service/SessionScopeService.kt:17` |
| `StressTestService` | service | core | Service | `ProjectionInputAssembler`, `BaselinePriceService`, `CoverRatioService` |  |  | `core/src/main/kotlin/harbor/service/StressTestService.kt:26` |
| `CoverRatioCalculator` | utils | core | object |  |  | `cover_ratio` | `core/src/main/kotlin/harbor/utils/CoverRatioCalculator.kt:23` |
| `MonthGrid` | utils | core | class |  |  |  | `core/src/main/kotlin/harbor/utils/MonthGrid.kt:13` |
| `PeerBenchmark` | utils | core | object |  |  | `peer_benchmark_simulation` | `core/src/main/kotlin/harbor/utils/PeerBenchmark.kt:19` |
| `ProjectionAggregator` | utils | core | object |  |  | `monthly_projection`, `horizon_totals` | `core/src/main/kotlin/harbor/utils/ProjectionAggregator.kt:36` |
| `RoleClassifier` | utils | core | object |  |  | `client_role_classification` | `core/src/main/kotlin/harbor/utils/RoleClassifier.kt:24` |
| `Rounding` | utils | core | object |  |  |  | `core/src/main/kotlin/harbor/utils/Rounding.kt:16` |
| `ScenarioPricePath` | utils | core | object |  |  | `scenario_price_path` | `core/src/main/kotlin/harbor/utils/ScenarioPricePath.kt:19` |
| `StressTestCalculator` | utils | core | object |  |  | `stress_test_monthly` | `core/src/main/kotlin/harbor/utils/StressTestCalculator.kt:23` |
| `MovementInputValidator` | validator | core | Component |  |  |  | `core/src/main/kotlin/harbor/validator/MovementInputValidator.kt:16` |
| `ParameterValidator` | validator | core | Component |  |  |  | `core/src/main/kotlin/harbor/validator/ParameterValidator.kt:16` |
| `RoleOverrideValidator` | validator | core | Component |  |  |  | `core/src/main/kotlin/harbor/validator/RoleOverrideValidator.kt:15` |
| `ScenarioValidator` | validator | core | Component |  |  |  | `core/src/main/kotlin/harbor/validator/ScenarioValidator.kt:15` |
