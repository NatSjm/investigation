import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { DimensionToggle } from './DimensionToggle';
import { defaultDimension } from '../stress.types';

describe('DimensionToggle', () => {
  it('renders both dimensions and marks the selected one', () => {
    const html = renderToStaticMarkup(<DimensionToggle value="CITY" onChange={() => undefined} />);
    expect(html).toContain('By city');
    expect(html).toContain('By transport mode');
    expect(html).toMatch(/aria-checked="true"[^>]*>By city/);
    expect(html).toMatch(/aria-checked="false"[^>]*>By transport mode/);
  });

  it('selects the transport mode segment when asked', () => {
    const html = renderToStaticMarkup(<DimensionToggle value="TRANSPORT_MODE" onChange={() => undefined} />);
    expect(html).toMatch(/aria-checked="true"[^>]*>By transport mode/);
  });

  it('disables both segments when disabled', () => {
    const html = renderToStaticMarkup(<DimensionToggle value="CITY" onChange={() => undefined} disabled />);
    expect(html.match(/disabled=""/g)).toHaveLength(2);
  });
});

describe('defaultDimension', () => {
  it('uses city for Product 1 and transport mode for Product 2', () => {
    expect(defaultDimension('product1')).toBe('CITY');
    expect(defaultDimension('product2')).toBe('TRANSPORT_MODE');
  });

  it('falls back to city when no product group is known', () => {
    expect(defaultDimension(null)).toBe('CITY');
    expect(defaultDimension(undefined)).toBe('CITY');
  });
});
