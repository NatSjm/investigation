/**
 * View-model types for the client-facing presentation window. FE-only: the screen mirrors the
 * representative's session pages and has no contract schema of its own; message shapes live in `channel.ts`.
 * @docs PRS-001
 */
import type { PresentationView } from './channel';

/** Which mirrored view the client screen shows; `waiting` covers routes without a client counterpart. */
export type PresentationStep = 'product1' | 'product2' | 'scenarios' | 'stress-test' | 'waiting';

/** State kept by `PresentationPage`: last route, merged filters and whether the session was closed. */
export interface PresentationState {
  route: string | null;
  view: PresentationView;
  closed: boolean;
}

const STEP_SUFFIX: ReadonlyArray<[suffix: string, step: PresentationStep]> = [
  ['/product1', 'product1'],
  ['/product2', 'product2'],
  ['/scenarios', 'scenarios'],
  ['/stress-test', 'stress-test'],
];

/** Maps a `/session/:sessionId/<step>` pathname to the mirrored step; summary and non-session routes -> `waiting`. */
export function stepFromPath(path: string | null): PresentationStep {
  if (!path) return 'waiting';
  const clean = path.replace(/\/+$/, '');
  return STEP_SUFFIX.find(([suffix]) => clean.endsWith(suffix))?.[1] ?? 'waiting';
}
