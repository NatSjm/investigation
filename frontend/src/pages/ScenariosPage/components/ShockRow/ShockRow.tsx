import type { Shock } from '@/types/market';

export interface ShockRowProps {
  index: number;
  shock: Shock;
  horizonMonths: number;
  onChange: (next: Shock) => void;
  onRemove: () => void;
}

/** One editable shock: month it starts, price change and transport price change (entered in %). */
export function ShockRow({ index, shock, horizonMonths, onChange, onRemove }: ShockRowProps) {
  const pct = (fraction: number) => String(Math.round(fraction * 1000) / 10);
  const fromPct = (text: string) => (Number(text) || 0) / 100;

  return (
    <tr className="shock-row">
      <td>{index + 1}</td>
      <td>
        <input
          type="number"
          min={1}
          max={horizonMonths}
          aria-label={`Shock ${index + 1} from month`}
          value={shock.fromMonth}
          onChange={(e) => onChange({ ...shock, fromMonth: Math.max(1, Math.min(horizonMonths, Number(e.target.value) || 1)) })}
        />
      </td>
      <td>
        <input
          type="number"
          step={0.5}
          aria-label={`Shock ${index + 1} price change %`}
          value={pct(shock.priceChangePct)}
          onChange={(e) => onChange({ ...shock, priceChangePct: fromPct(e.target.value) })}
        />
      </td>
      <td>
        <input
          type="number"
          step={0.5}
          aria-label={`Shock ${index + 1} transport change %`}
          value={pct(shock.transportChangePct)}
          onChange={(e) => onChange({ ...shock, transportChangePct: fromPct(e.target.value) })}
        />
      </td>
      <td>
        <button type="button" className="link" aria-label={`Remove shock ${index + 1}`} onClick={onRemove}>
          Remove
        </button>
      </td>
    </tr>
  );
}
