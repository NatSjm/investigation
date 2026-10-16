import { DIMENSION_LABEL, type Dimension } from '@/types/stress';

export interface DimensionToggleProps {
  value: Dimension;
  onChange: (next: Dimension) => void;
  disabled?: boolean;
}

const OPTIONS: Dimension[] = ['CITY', 'TRANSPORT_MODE'];

/** Segmented control switching the stress table between city and transport mode breakdown. */
export function DimensionToggle({ value, onChange, disabled }: DimensionToggleProps) {
  return (
    <div className="dimension-toggle" role="radiogroup" aria-label="Breakdown dimension">
      {OPTIONS.map((d) => (
        <button
          key={d}
          type="button"
          role="radio"
          aria-checked={value === d}
          className={value === d ? 'segment active' : 'segment'}
          disabled={disabled}
          onClick={() => value !== d && onChange(d)}
        >
          {DIMENSION_LABEL[d]}
        </button>
      ))}
    </div>
  );
}
