import { TRANSPORT_MODE_LABEL, type TransportMode } from '@/types/product2';

export interface TransportModeSelectorProps {
  value: TransportMode | undefined;
  options: readonly TransportMode[];
  onChange: (mode: TransportMode | undefined) => void;
}

/** Transport mode filter for Product 2 tables (ROAD, RAIL, SEA, AIR or all). */
export function TransportModeSelector({ value, options, onChange }: TransportModeSelectorProps) {
  return (
    <label className="dimension-selector">
      Transport mode
      <select value={value ?? ''} onChange={(e) => onChange((e.target.value || undefined) as TransportMode | undefined)}>
        <option value="">All modes</option>
        {options.map((m) => (
          <option key={m} value={m}>
            {TRANSPORT_MODE_LABEL[m]}
          </option>
        ))}
      </select>
    </label>
  );
}
