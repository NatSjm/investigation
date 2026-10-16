import { describe, expect, it } from 'vitest';
import { SESSION_CHANNEL_PREFIX, sessionChannelName } from '@/components/broadcast/sessionChannel';
import { stepFromPath } from '@/types/presentation';

describe('sessionChannelName', () => {
  it('derives one channel per session under the harbor.session prefix', () => {
    expect(SESSION_CHANNEL_PREFIX).toBe('harbor.session');
    expect(sessionChannelName('11111111-2222-3333-4444-555555555555')).toBe('harbor.session.11111111-2222-3333-4444-555555555555');
  });
});

describe('stepFromPath', () => {
  const base = '/session/11111111-2222-3333-4444-555555555555';

  it('maps the session sub-pages to their mirrored step', () => {
    expect(stepFromPath(`${base}/product1`)).toBe('product1');
    expect(stepFromPath(`${base}/product2/`)).toBe('product2');
    expect(stepFromPath(`${base}/scenarios`)).toBe('scenarios');
    expect(stepFromPath(`${base}/stress-test`)).toBe('stress-test');
  });

  it('falls back to waiting for routes without a client counterpart', () => {
    expect(stepFromPath(null)).toBe('waiting');
    expect(stepFromPath(`${base}/summary`)).toBe('waiting');
    expect(stepFromPath('/clients')).toBe('waiting');
  });
});
