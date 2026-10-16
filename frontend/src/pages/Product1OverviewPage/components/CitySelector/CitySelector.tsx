export interface CitySelectorProps {
  value: string | undefined;
  options: readonly string[];
  onChange: (city: string | undefined) => void;
}

/** City hub filter for Product 1 tables (Aldmoor, Brightwater, Carrow, Dunmere or all). */
export function CitySelector({ value, options, onChange }: CitySelectorProps) {
  return (
    <label className="dimension-selector">
      City hub
      <select value={value ?? ''} onChange={(e) => onChange(e.target.value || undefined)}>
        <option value="">All cities</option>
        {options.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>
    </label>
  );
}
