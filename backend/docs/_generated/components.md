---
type: Document
title: "Components (BE)"
description: "One row per class: layer, stereotype, injected dependencies, tables, @docs tags and file:line; business context = class-name prefix."
generated:
  by: process:gen-docs
  at: 2026-10-16
status: stable
---
# Components (BE)

> Generated from `top-level Kotlin declarations per layer` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
157 declaration(s). Per layer: (root) 2, advice 1, api 10, api/error 1, api/technical 1, client/kafka 3, client/rest 5, component 8, config 4, context 3, dao/mapper 1, dao/model 16, dao/repository 17, dao/service 1, dao/specification 1, databind 2, enums 15, event 9, exception 6, job 2, manager 10, mapper 9, model 3, service 15, utils 8, validator 4. Business context of a class = its name prefix (docs repo `contexts.yml`).

| Class | Layer | Module | Kind | Depends on | Tables | @docs | Location |
|---|---|---|---|---|---|---|---|
| `HarborBackendApplication` | (root) | harbor-core | SpringBootApplication |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/HarborBackendApplication.kt:14` |
| `HarborConstants` | (root) | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/HarborConstants.kt:4` |
| `GlobalExceptionAdvice` | advice | harbor-core | RestControllerAdvice |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/advice/GlobalExceptionAdvice.kt:33` |
| `AdminController` | api | harbor-core | RestController | `AdminManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/AdminController.kt:17` |
| `ClientController` | api | harbor-core | RestController | `ClientManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/ClientController.kt:20` |
| `CoverController` | api | harbor-core | RestController | `CoverManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/CoverController.kt:20` |
| `HttpHeadersFactory` | api | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/HttpHeadersFactory.kt:8` |
| `Product1Controller` | api | harbor-core | RestController | `Product1Manager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product1Controller.kt:21` |
| `Product2Controller` | api | harbor-core | RestController | `Product2Manager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product2Controller.kt:22` |
| `ReportController` | api | harbor-core | RestController | `ReportManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/ReportController.kt:18` |
| `ScenarioController` | api | harbor-core | RestController | `MarketManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/ScenarioController.kt:20` |
| `SessionController` | api | harbor-core | RestController | `MeetingManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/SessionController.kt:22` |
| `StressTestController` | api | harbor-core | RestController | `StressManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/StressTestController.kt:18` |
| `ProblemDetails` | api/error | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/error/ProblemDetails.kt:12` |
| `TechnicalController` | api/technical | harbor-core | RestController |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/technical/TechnicalController.kt:14` |
| `AvroJsonDeserializer` | client/kafka | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/client/kafka/AvroJsonSerde.kt:30` |
| `AvroJsonSerializer` | client/kafka | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/client/kafka/AvroJsonSerde.kt:17` |
| `EventProducer` | client/kafka | harbor-core | Component, KafkaProducer |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/client/kafka/EventProducer.kt:11` |
| `ClientRegistryClient` | client/rest | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/client/rest/ClientRegistryClient.kt:16` |
| `CoverProviderClient` | client/rest | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/client/rest/CoverProviderClient.kt:19` |
| `DocumentServiceClient` | client/rest | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/client/rest/DocumentServiceClient.kt:17` |
| `FileExchangeClient` | client/rest | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/client/rest/FileExchangeClient.kt:17` |
| `MarketDataClient` | client/rest | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/client/rest/MarketDataClient.kt:19` |
| `ReportTemplateLoader` | component | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/component/ReportTemplateLoader.kt:15` |
| `SessionHeaderFilter` | component | harbor-core | Component | `MeetingSessionDaoService`, `SessionScopeService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/component/SessionHeaderFilter.kt:33` |
| `StatisticalViewsInitializer` | component | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/component/StatisticalViewsInitializer.kt:15` |
| `WorkbookDelimitedReader` | component | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/component/WorkbookDelimitedReader.kt:7` |
| `WorkbookReader` | component | harbor-core | interface |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/component/WorkbookReader.kt:9` |
| `WorkbookReaderFactory` | component | harbor-core | Component | `XlsWorkbookOpener` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/component/WorkbookReaderFactory.kt:11` |
| `XlsMovementParser` | component | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/component/XlsMovementParser.kt:32` |
| `XlsWorkbookOpener` | component | harbor-core | interface |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/component/XlsWorkbookOpener.kt:8` |
| `JacksonConfig` | config | harbor-core | Configuration |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/config/JacksonConfig.kt:17` |
| `KafkaConfig` | config | harbor-core | Configuration |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/config/KafkaConfig.kt:48` |
| `SchedulingConfig` | config | harbor-core | Configuration |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/config/SchedulingConfig.kt:18` |
| `WebConfig` | config | harbor-core | Configuration |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/config/WebConfig.kt:17` |
| `CurrentUser` | context | harbor-core | interface |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/context/CurrentUser.kt:7` |
| `SessionContext` | context | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/context/SessionContext.kt:12` |
| `SessionScope` | context | harbor-core | class | `ProductGroup`, `SessionKind`, `PriceBasis`, `ClientRole` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/context/SessionScope.kt:13` |
| `ProjectionRowMapper` | dao/mapper | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/mapper/ProjectionRowMapper.kt:9` |
| `BaselinePrice` | dao/model | harbor-core | Entity | `ProductGroup` | `baseline_price` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/BaselinePrice.kt:20` |
| `ClientProfile` | dao/model | harbor-core | Entity |  | `client_profile` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/ClientProfile.kt:14` |
| `ClientRoleDecision` | dao/model | harbor-core | Entity | `ProductGroup`, `ClientRole`, `RoleSource` | `client_role` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/ClientRoleDecision.kt:22` |
| `CoverPolicy` | dao/model | harbor-core | Entity | `ProductGroup` | `cover_policy` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/CoverPolicy.kt:21` |
| `CoverQuote` | dao/model | harbor-core | Entity |  | `cover_quote` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/CoverQuote.kt:12` |
| `GoodsMovement` | dao/model | harbor-core | Entity | `ProductGroup`, `TransportMode`, `Direction`, `PriceBasis` | `goods_movement` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/GoodsMovement.kt:23` |
| `ImportBatch` | dao/model | harbor-core | Entity | `ImportStatus` | `import_batch` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/ImportBatch.kt:14` |
| `MarketScenario` | dao/model | harbor-core | Entity | `ScenarioKind` | `market_scenario` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/MarketScenario.kt:21` |
| `MeetingReport` | dao/model | harbor-core | Entity | `ReportStatus` | `meeting_report` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/MeetingReport.kt:19` |
| `MeetingSession` | dao/model | harbor-core | Entity | `ProductGroup`, `SessionKind`, `SessionStatus`, `ClientRole` | `meeting_session` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/MeetingSession.kt:25` |
| `MovementMonthly` | dao/model | harbor-core | Entity | `ProductGroup`, `TransportMode`, `Direction` | `movement_monthly` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/MovementMonthly.kt:22` |
| `Parameter` | dao/model | harbor-core | Entity | `ProductGroup` | `parameter_set` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/Parameter.kt:20` |
| `SessionClientConfig` | dao/model | harbor-core | Entity | `PriceBasis`, `CoverPreference` | `session_client_config` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/SessionClientConfig.kt:17` |
| `SessionMovementInput` | dao/model | harbor-core | Entity | `TransportMode`, `Direction` | `session_movement_input` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/SessionMovementInput.kt:20` |
| `SessionPeerSimulation` | dao/model | harbor-core | Entity |  | `session_peer_simulation` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/SessionPeerSimulation.kt:15` |
| `StressTestResult` | dao/model | harbor-core | Entity |  | `stress_test_result` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/model/StressTestResult.kt:17` |
| `BaselinePriceRepository` | dao/repository | harbor-core | Repository |  | `baseline_price` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/BaselinePriceRepository.kt:10` |
| `ClientProfileRepository` | dao/repository | harbor-core | Repository |  | `client_profile` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/ClientProfileRepository.kt:10` |
| `ClientRoleRepository` | dao/repository | harbor-core | Repository |  | `client_role` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/ClientRoleRepository.kt:10` |
| `CoverPolicyRepository` | dao/repository | harbor-core | Repository |  | `cover_policy` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/CoverPolicyRepository.kt:10` |
| `CoverQuoteRepository` | dao/repository | harbor-core | Repository |  | `cover_quote` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/CoverQuoteRepository.kt:9` |
| `GoodsMovementRepository` | dao/repository | harbor-core | Repository |  | `movement_monthly`, `goods_movement` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/GoodsMovementRepository.kt:12` |
| `ImportBatchRepository` | dao/repository | harbor-core | Repository |  | `import_batch` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/ImportBatchRepository.kt:9` |
| `MarketScenarioRepository` | dao/repository | harbor-core | Repository |  | `market_scenario` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/MarketScenarioRepository.kt:9` |
| `MeetingReportRepository` | dao/repository | harbor-core | Repository |  | `meeting_report` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/MeetingReportRepository.kt:9` |
| `MeetingSessionRepository` | dao/repository | harbor-core | Repository |  | `meeting_session` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/MeetingSessionRepository.kt:13` |
| `MovementMonthlyRepository` | dao/repository | harbor-core | Repository |  | `movement_monthly` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/MovementMonthlyRepository.kt:13` |
| `ParameterRepository` | dao/repository | harbor-core | Repository |  | `parameter_set` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/ParameterRepository.kt:12` |
| `ProjectionRepository` | dao/repository | harbor-core | Repository |  | `projection_by_subproduct`, `projection_by_dimension`, `projection_by_direction`, `projection_summary` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/ProjectionRepository.kt:23` |
| `SessionClientConfigRepository` | dao/repository | harbor-core | Repository |  | `session_client_config` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/SessionClientConfigRepository.kt:9` |
| `SessionMovementInputRepository` | dao/repository | harbor-core | Repository |  | `session_movement_input` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/SessionMovementInputRepository.kt:10` |
| `SessionPeerSimulationRepository` | dao/repository | harbor-core | Repository |  | `session_peer_simulation` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/SessionPeerSimulationRepository.kt:9` |
| `StressTestResultRepository` | dao/repository | harbor-core | Repository |  | `stress_test_result` |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/repository/StressTestResultRepository.kt:10` |
| `MeetingSessionDaoService` | dao/service | harbor-core | Service | `MeetingSessionRepository` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/service/MeetingSessionDaoService.kt:19` |
| `MeetingSessionSpecifications` | dao/specification | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/dao/specification/MeetingSessionSpecifications.kt:10` |
| `MoneySerializer` | databind | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/databind/MoneySerializer.kt:12` |
| `PeriodDeserializer` | databind | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/databind/PeriodDeserializer.kt:14` |
| `ClientRole` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/ClientRole.kt:4` |
| `CoverPreference` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/CoverPreference.kt:4` |
| `DimensionKind` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/DimensionKind.kt:4` |
| `Direction` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/Direction.kt:4` |
| `ImportStatus` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/ImportStatus.kt:4` |
| `ParameterKey` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/ParameterKey.kt:4` |
| `PriceBasis` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/PriceBasis.kt:4` |
| `ProductGroup` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/ProductGroup.kt:7` |
| `ReportStatus` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/ReportStatus.kt:4` |
| `RoleSource` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/RoleSource.kt:4` |
| `ScenarioKind` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/ScenarioKind.kt:4` |
| `SessionKind` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/SessionKind.kt:4` |
| `SessionStatus` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/SessionStatus.kt:4` |
| `StressDimension` | enums | harbor-core | class | `DimensionKind` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/StressDimension.kt:7` |
| `TransportMode` | enums | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/enums/TransportMode.kt:4` |
| `ClientRoleSessionClosedListener` | event | harbor-core | Component, KafkaListener | `ClientRoleService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/ClientRoleSessionClosedListener.kt:18` |
| `MarketPricesListener` | event | harbor-core | Component, KafkaListener | `BaselinePriceService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/MarketPricesListener.kt:17` |
| `MovementsLoadedPublisher` | event | harbor-core | Component, KafkaProducer | `EventProducer`, `GoodsMovementRepository` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/MovementsLoadedPublisher.kt:14` |
| `Product1ProjectionRefreshListener` | event | harbor-core | Component, KafkaListener | `SessionScopeService`, `ProjectionService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/Product1ProjectionRefreshListener.kt:17` |
| `Product2ProjectionRefreshListener` | event | harbor-core | Component, KafkaListener | `SessionScopeService`, `ProjectionService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/Product2ProjectionRefreshListener.kt:17` |
| `ReportRenderedListener` | event | harbor-core | Component, KafkaListener | `ReportManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/ReportRenderedListener.kt:9` |
| `ReportRenderRequester` | event | harbor-core | Component, KafkaProducer | `EventProducer`, `ReportTemplateLoader` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/ReportRenderRequester.kt:15` |
| `ReportSessionClosedListener` | event | harbor-core | Component, KafkaListener | `ReportManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/ReportSessionClosedListener.kt:14` |
| `SessionEventsPublisher` | event | harbor-core | Component, KafkaProducer | `EventProducer` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/event/SessionEventsPublisher.kt:13` |
| `MissingParameterException` | exception | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/exception/MissingParameterException.kt:6` |
| `NotFoundException` | exception | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/exception/NotFoundException.kt:4` |
| `SessionClosedException` | exception | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/exception/SessionClosedException.kt:6` |
| `SessionHeaderMissingException` | exception | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/exception/SessionHeaderMissingException.kt:4` |
| `SessionNotBoundException` | exception | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/exception/SessionNotBoundException.kt:4` |
| `ValidationException` | exception | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/exception/ValidationException.kt:4` |
| `DailyMovementImportJob` | job | harbor-core | Component, Scheduled | `ImportManager` | `goods_movement` |  | `harbor-core/src/main/kotlin/com/acme/harbor/job/DailyMovementImportJob.kt:13` |
| `MonthlySnapshotJob` | job | harbor-core | Component, Scheduled | `ImportManager` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/job/MonthlySnapshotJob.kt:15` |
| `AdminManager` | manager | harbor-core | Service | `ParameterService`, `ParameterValidator`, `MovementImportService`, `CurrentUser` |  | `ADM-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/AdminManager.kt:24` |
| `ClientManager` | manager | harbor-core | Service | `ClientProfileService`, `ClientRoleRepository`, `ClientRoleService`, `ClientOverviewService` |  | `CLI-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/ClientManager.kt:25` |
| `CoverManager` | manager | harbor-core | Service | `CoverPolicyRepository`, `ProjectionService`, `CoverRatioService`, `CoverQuoteService`, `ClientProfileService` |  | `COV-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/CoverManager.kt:25` |
| `ImportManager` | manager | harbor-core | Service | `MovementImportService` |  | `IMP-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/ImportManager.kt:18` |
| `MarketManager` | manager | harbor-core | Service | `ScenarioService`, `BaselinePriceService` |  | `MKT-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/MarketManager.kt:21` |
| `MeetingManager` | manager | harbor-core | Service | `MeetingSessionRepository`, `MeetingSessionDaoService`, `SessionClientConfigRepository`, `ClientProfileService`, `ParameterService`, `RoleOverrideValidator`, `SessionEventsPublisher`, `CurrentUser` |  | `SES-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/MeetingManager.kt:38` |
| `Product1Manager` | manager | harbor-core | Service | `ProjectionService`, `ProjectionInputAssembler`, `PeerSimulationService`, `ClientRoleService`, `MovementInputValidator` |  | `P1-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/Product1Manager.kt:26` |
| `Product2Manager` | manager | harbor-core | Service | `ProjectionService`, `ProjectionInputAssembler`, `PeerSimulationService`, `ClientRoleService`, `MovementInputValidator` |  | `P2-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/Product2Manager.kt:26` |
| `ReportManager` | manager | harbor-core | Service | `MeetingReportRepository`, `MeetingSessionRepository`, `MeetingSessionDaoService`, `ReportPayloadService`, `ReportRenderRequester`, `DocumentServiceClient` |  | `RPT-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/ReportManager.kt:27` |
| `StressManager` | manager | harbor-core | Service | `StressTestService`, `StressTestResultRepository`, `MarketScenarioRepository`, `ClientRoleService` |  | `STR-001` | `harbor-core/src/main/kotlin/com/acme/harbor/manager/StressManager.kt:30` |
| `ClientMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/ClientMapper.kt:21` |
| `CoverMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/CoverMapper.kt:18` |
| `ImportBatchMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/ImportBatchMapper.kt:8` |
| `ParameterMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/ParameterMapper.kt:12` |
| `ProjectionMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/ProjectionMapper.kt:31` |
| `ReportMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/ReportMapper.kt:9` |
| `ScenarioMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/ScenarioMapper.kt:18` |
| `SessionMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/SessionMapper.kt:17` |
| `StressMapper` | mapper | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/mapper/StressMapper.kt:14` |
| `ClientOverviewIndicators` | model | harbor-core | class | `ProductGroup`, `ClientRole` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/model/ClientOverviewIndicators.kt:13` |
| `ProjectionRow` | model | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/model/ProjectionRow.kt:11` |
| `ScenarioShock` | model | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/model/ScenarioShock.kt:7` |
| `BaselinePriceService` | service | harbor-core | Service | `BaselinePriceRepository`, `MarketDataClient` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/BaselinePriceService.kt:23` |
| `ClientOverviewService` | service | harbor-core | Service | `MovementMonthlyRepository`, `MeetingSessionRepository`, `ClientRoleService`, `CoverRatioService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/ClientOverviewService.kt:23` |
| `ClientProfileService` | service | harbor-core | Service | `ClientProfileRepository`, `ClientRegistryClient` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/ClientProfileService.kt:16` |
| `ClientRoleService` | service | harbor-core | Service | `ClientRoleRepository`, `MovementMonthlyRepository`, `ParameterService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/ClientRoleService.kt:28` |
| `CoverQuoteService` | service | harbor-core | Service | `CoverQuoteRepository`, `CoverProviderClient`, `ParameterService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/CoverQuoteService.kt:23` |
| `CoverRatioService` | service | harbor-core | Service | `CoverPolicyRepository`, `MovementMonthlyRepository` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/CoverRatioService.kt:26` |
| `MovementImportService` | service | harbor-core | Service | `ImportBatchRepository`, `GoodsMovementRepository`, `MovementMonthlyRepository`, `FileExchangeClient`, `WorkbookReaderFactory`, `XlsMovementParser`, `MovementsLoadedPublisher`, `ClientProfileService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/MovementImportService.kt:31` |
| `ParameterService` | service | harbor-core | Service | `ParameterRepository` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/ParameterService.kt:23` |
| `PeerSimulationService` | service | harbor-core | Service | `MovementMonthlyRepository`, `SessionPeerSimulationRepository`, `ParameterService` |  | `P1-003`, `P2-003` | `harbor-core/src/main/kotlin/com/acme/harbor/service/PeerSimulationService.kt:26` |
| `ProjectionInputAssembler` | service | harbor-core | Component | `MovementMonthlyRepository`, `SessionMovementInputRepository`, `ParameterService`, `BaselinePriceService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/ProjectionInputAssembler.kt:30` |
| `ProjectionService` | service | harbor-core | Service | `ProjectionInputAssembler`, `ProjectionRepository`, `SessionMovementInputRepository`, `CoverRatioService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/ProjectionService.kt:27` |
| `ReportPayloadService` | service | harbor-core | Service | `MeetingSessionDaoService`, `SessionClientConfigRepository`, `ClientProfileService`, `ProjectionRepository`, `MarketScenarioRepository`, `StressTestResultRepository` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/ReportPayloadService.kt:22` |
| `ScenarioService` | service | harbor-core | Service | `MarketScenarioRepository`, `ScenarioValidator` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/ScenarioService.kt:20` |
| `SessionScopeService` | service | harbor-core | Service | `MeetingSessionRepository`, `MeetingSessionDaoService`, `SessionClientConfigRepository` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/SessionScopeService.kt:18` |
| `StressTestService` | service | harbor-core | Service | `ProjectionInputAssembler`, `BaselinePriceService`, `CoverRatioService` |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/service/StressTestService.kt:26` |
| `CoverRatioCalculator` | utils | harbor-core | object |  |  | `cover_ratio` | `harbor-core/src/main/kotlin/com/acme/harbor/utils/CoverRatioCalculator.kt:23` |
| `MonthGrid` | utils | harbor-core | class |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/utils/MonthGrid.kt:13` |
| `PeerBenchmark` | utils | harbor-core | object |  |  | `peer_benchmark_simulation` | `harbor-core/src/main/kotlin/com/acme/harbor/utils/PeerBenchmark.kt:19` |
| `ProjectionAggregator` | utils | harbor-core | object |  |  | `monthly_projection`, `horizon_totals` | `harbor-core/src/main/kotlin/com/acme/harbor/utils/ProjectionAggregator.kt:36` |
| `RoleClassifier` | utils | harbor-core | object |  |  | `client_role_classification` | `harbor-core/src/main/kotlin/com/acme/harbor/utils/RoleClassifier.kt:24` |
| `Rounding` | utils | harbor-core | object |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/utils/Rounding.kt:16` |
| `ScenarioPricePath` | utils | harbor-core | object |  |  | `scenario_price_path` | `harbor-core/src/main/kotlin/com/acme/harbor/utils/ScenarioPricePath.kt:19` |
| `StressTestCalculator` | utils | harbor-core | object |  |  | `stress_test_monthly` | `harbor-core/src/main/kotlin/com/acme/harbor/utils/StressTestCalculator.kt:23` |
| `MovementInputValidator` | validator | harbor-core | Component |  |  | `P1-002`, `P2-002` | `harbor-core/src/main/kotlin/com/acme/harbor/validator/MovementInputValidator.kt:18` |
| `ParameterValidator` | validator | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/validator/ParameterValidator.kt:16` |
| `RoleOverrideValidator` | validator | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/validator/RoleOverrideValidator.kt:15` |
| `ScenarioValidator` | validator | harbor-core | Component |  |  |  | `harbor-core/src/main/kotlin/com/acme/harbor/validator/ScenarioValidator.kt:15` |
