# Update Log

## 2026-10-15
* **[SES-001](SES-001.md)**: Spec prefix renamed `MTG` → `SES` (file `MTG-001.md` → `SES-001.md`, rules `BR-MTG-001-n` → `BR-SES-001-n`, dataset `mtg-session-snapshot` → `ses-session-snapshot`); the context folder stays `meetings`

## 2026-10-12
* **[SES-001](SES-001.md)**: Meetings list split into `/meetings/client` (kind CLIENT) and `/meetings/preparation` (kind PREPARATION), `/meetings` redirects to the client list; closing a session publishes `session-closed` on the presentation channel (PRS-001) (fe routes.tsx, useCloseSession.ts)

## 2026-10-09
* **[SES-001](SES-001.md)**: Rebuilt for the Harbor bundle
