---
type: Flow
title: Client presentation flow (two windows, one session)
description: How the representative's session window and the client-facing presentation window stay in step over the BroadcastChannel harbor.session.<sessionId>, from opening the second window to closing the session.
tags: [flow, presentation, meetings, product1, product2, market, stress]
status: draft
generated: { by: copilot/spec-writer, at: 2026-10-12T00:30:00Z }
stale_after: 2027-01-10T00:00:00Z
sources:
  - id: channel
    resource: fe/src/features/presentation/channel.ts
    title: channel.ts
# --- repo extensions ---
id: FLOW-client-presentation
contexts: [meetings, presentation, product1, product2, market, stress]
specs: [MTG-001, PRS-001, P1-001, STR-001]
code_refs:
  - fe/src/app/SessionLayout.tsx
  - fe/src/features/presentation/channel.ts
  - fe/src/features/presentation/ui/PresentationPage.tsx
  - fe/src/features/meetings/api/useCloseSession.ts
channels: ["harbor.session.{sessionId}"]
---

# Client presentation flow (two windows, one session)

## Purpose
A meeting has two audiences in one browser: the representative, who navigates and models, and the client, who must
see the results on a second screen without the internal controls. This flow describes how the two windows stay in
step without any backend involvement. Rules live in PRS-001; this document composes them with MTG-001 (session
lifecycle) and the product and stress pages that publish their filters.

## Questions this document answers
- What happens, step by step, when the representative presses "Open client screen"?
- Which window publishes which message, and which component reacts?
- What does the client see while nothing has been published, and after the session is closed?
- Why does a client window opened late still show the right page?

## Trigger
The representative is inside an OPEN CLIENT session (`/session/:sessionId/*`) and presses "Open client screen" in
`SessionLayout`. Precondition: the session exists and is OPEN (MTG-001).

## Participants
| Participant | Kind | Role in the flow |
|---|---|---|
| `feature:fe-app` (`SessionLayout`) | FE app shell | publishes `route`; opens the second window |
| `feature:product1`, `feature:product2`, `feature:stress` | FE features | publish `view` slices |
| `feature:meetings` (`useCloseSession`) | FE feature | publishes `session-closed` |
| `channel:harbor.session.{*}` | browser channel | one per session, same origin |
| `feature:presentation` (`PresentationPage`, mirrors) | FE feature | subscribes, sends `hello`, renders read-only counterparts |
| `endpoint:GET /api/v1/sessions/{sessionId}` and the session-scoped reads | BE | serve both windows identically |

## Steps
```mermaid
sequenceDiagram
  participant R as Session window
  participant C as channel harbor.session.id
  participant P as Presentation window
  participant B as Backend
  R->>P: window.open('/present/id', noopener)
  P->>B: GET /sessions/id (session store: product group, status)
  P->>C: hello
  C-->>R: hello
  R->>C: replay last route / view (/ session-closed)
  C-->>P: route, view
  P->>B: GET /session/product1/overview?city=... (X-Harbor-Session: id)
  R->>C: route (on every navigation)
  R->>C: view (city / transport mode / dimension change)
  C-->>P: route, view -> re-render mirror
  R->>B: POST /sessions/id/close
  R->>C: session-closed
  C-->>P: "Session closed"
```
1. `SessionLayout` opens `/present/<id>` (`fe/src/app/SessionLayout.tsx`). The new window mounts
   `PresentationLayout` (`src/app/PresentationLayout.tsx:13`) and `PresentationPage` (`src/features/presentation/ui/PresentationPage.tsx:20`).
2. `PresentationLayout` loads the session (`useSession`) and initialises the window's session store so that
   `sessionHeader()` works there.
3. `usePresentationSubscriber` (`channel.ts:95`) opens the channel and sends `hello`.
4. Every `usePresentationPublisher` instance (`channel.ts:55`) answers `hello` by replaying its last message per type.
5. `PresentationPage` maps the `route` to a step (`stepFromPath`, `presentation.types.ts`) and renders the mirror with the
   published filters; the mirror fetches through the normal hooks.
6. Each navigation or filter change in the session window publishes again; the mirror re-renders.
7. `useCloseSession` publishes `session-closed` after the backend confirmed the close; the mirror shows "Session closed".

## Data and state changes
No persistent data. Window state: `PresentationState { route, view, closed }` in the presentation window; the
publishers keep the last message per type in memory for replay.

## Failure behaviour
- Backend error on a mirrored read: the mirror shows its loading / error text; the representative's window is unaffected.
- Presentation window closed by the client: nothing happens on the representative's side; a new window catches up via `hello`.
- Message with an unknown shape or unknown filter value: ignored or treated as "all" (BR-PRS-001-7).

## Invariants and assumptions
- Only `channel.ts` opens a `BroadcastChannel` (BR-PRS-001-2); the generated map `generated/fe/codebase-map.md` column
  Channels shows every publisher and subscriber.
- The two windows share origin and browser profile; a separate device needs a relayed variant (open question in PRS-001).
- The client window never shows controls or internal indicators (BR-PRS-001-1, BR-PRS-001-9).

## Security and privacy notes
Nothing internal crosses the boundary by design: the channel carries routes and filter values only; the client
window fetches its data itself through the same authorised session. Whether the client screen needs a weaker
authorisation than the representative's is an open question in PRS-001.

## Source map
| Concern | Location |
|---|---|
| Channel, message types, hooks | `fe/src/features/presentation/channel.ts` |
| Step mapping, window state | `fe/src/features/presentation/presentation.types.ts` |
| Mirrors | `fe/src/features/presentation/ui/{PresentationPage,ProductMirror,ScenariosMirror,StressMirror}.tsx` |
| Publishers | `fe/src/app/SessionLayout.tsx`, `fe/src/features/product1/ui/Product1OverviewPage.tsx`, `fe/src/features/product2/ui/Product2OverviewPage.tsx`, `fe/src/features/stress/ui/StressTestPage.tsx`, `fe/src/features/meetings/api/useCloseSession.ts` |
| Routes | `fe/src/app/routes.tsx:45` |

## Open questions
- [ ] Should the representative see a "client screen connected" indicator (requires a reply message from the subscriber)?

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-12 | Created with PRS-001 | — |
