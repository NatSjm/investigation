/**
 * @module presentation — Client-facing presentation window: read-only mirror of the representative's session steps, synchronised over a BroadcastChannel.
 * Second-screen view of a CLIENT session (`/present/:sessionId`): follows the representative's route and filters without any internal controls.
 * @docs PRS-001
 */
export { PresentationPage } from './ui/PresentationPage';
export { ProductMirror } from './ui/ProductMirror';
export { ScenariosMirror } from './ui/ScenariosMirror';
export { StressMirror } from './ui/StressMirror';
export { SESSION_CHANNEL_PREFIX, sessionChannelName, usePresentationPublisher, usePresentationSubscriber } from './channel';
export type { PresentationMessage, PresentationView } from './channel';
export type { PresentationStep, PresentationState } from './presentation.types';
export { stepFromPath } from './presentation.types';
