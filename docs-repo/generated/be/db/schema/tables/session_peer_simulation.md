---
type: Document
title: "session_peer_simulation"
description: "Peer simulation requested in a session: the peer segment and the scaling factor applied to the projection of the client."
generated:
  by: process:db-docs
  at: 2026-10-28
status: stable
---
# session_peer_simulation

Peer simulation requested in a session: the peer segment and the scaling factor applied to the projection of the client.

Created in `harbor-core/src/main/resources/db/migration/V4__session_inputs.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `peer_segment` | varchar(64) | no |  |  |  |
| `scaling_factor` | numeric(8, 4) | no |  |  | Factor applied to the quantities of the client to simulate a peer of the chosen segment. |
| `generated_at` | timestamp | no |  |  |  |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)

## Constraints

- check `ck_session_peer_simulation_scaling`: `(scaling_factor > 0)`
