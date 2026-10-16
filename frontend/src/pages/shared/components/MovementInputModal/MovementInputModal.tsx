import { useState } from 'react';
import { errorMessage } from '@/services/api/client';
import { Modal } from '@/components/Modal';
import { formatPeriod } from '@/utils/months';
import type { Direction, MovementDimension, MovementInput } from '@/types/product1';

export interface MovementInputModalProps {
  open: boolean;
  onClose: () => void;
  /** Projection grid of the session (`projectionGrid(horizon)`): the months the backend accepts. */
  periods: string[];
  subProducts: readonly string[];
  /** `city` for Product 1, `transportMode` for Product 2. */
  dimension: MovementDimension;
  dimensionValues: readonly string[];
  initial?: MovementInput[];
  pending?: boolean;
  onSubmit: (movements: MovementInput[]) => Promise<unknown> | void;
}

type Draft = { quantity: string; unitPrice: string };

const draftKey = (period: string, direction: Direction) => `${period}|${direction}`;

/**
 * Modal 1: modelled movements per month. One row per month with IN and OUT quantity / unit price
 * for the chosen sub-product and dimension value; empty cells are not sent.
 * @docs P1-002
 */
export function MovementInputModal({ open, onClose, periods, subProducts, dimension, dimensionValues, initial = [], pending, onSubmit }: MovementInputModalProps) {
  const [subProduct, setSubProduct] = useState<string>(subProducts[0] ?? '');
  const [dimensionValue, setDimensionValue] = useState<string>(dimensionValues[0] ?? '');
  const [error, setError] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Record<string, Draft>>(() => {
    const seed: Record<string, Draft> = {};
    for (const m of initial) seed[draftKey(m.period, m.direction)] = { quantity: String(m.quantity), unitPrice: String(m.unitPrice) };
    return seed;
  });

  const edit = (period: string, direction: Direction, field: keyof Draft, value: string) =>
    setDrafts((prev) => ({ ...prev, [draftKey(period, direction)]: { ...(prev[draftKey(period, direction)] ?? { quantity: '', unitPrice: '' }), [field]: value } }));

  const toMovements = (): MovementInput[] =>
    Object.entries(drafts).flatMap(([key, d]) => {
      const [period, direction] = key.split('|') as [string, Direction];
      const quantity = Number(d.quantity);
      const unitPrice = Number(d.unitPrice);
      if (!quantity || Number.isNaN(unitPrice)) return [];
      const base: MovementInput = { period, subProduct, direction, quantity, unitPrice };
      return [dimension === 'city' ? { ...base, city: dimensionValue } : { ...base, transportMode: dimensionValue as MovementInput['transportMode'] }];
    });

  const submit = async () => {
    setError(null);
    try {
      await onSubmit(toMovements());
      onClose();
    } catch (e) {
      setError(errorMessage(e));
    }
  };

  const cell = (period: string, direction: Direction, field: keyof Draft) => (
    <input
      type="number"
      min={0}
      step={field === 'quantity' ? 1 : 0.01}
      aria-label={`${formatPeriod(period)} ${direction} ${field}`}
      value={drafts[draftKey(period, direction)]?.[field] ?? ''}
      onChange={(e) => edit(period, direction, field, e.target.value)}
    />
  );

  return (
    <Modal
      open={open}
      title="Modelled movements"
      onClose={onClose}
      width={860}
      footer={
        <>
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="button" className="primary" disabled={pending} onClick={submit}>Save and recompute</button>
        </>
      }
    >
      <div className="modal-controls">
        <label>
          Sub-product
          <select value={subProduct} onChange={(e) => setSubProduct(e.target.value)}>
            {subProducts.map((s) => <option key={s}>{s}</option>)}
          </select>
        </label>
        <label>
          {dimension === 'city' ? 'City hub' : 'Transport mode'}
          <select value={dimensionValue} onChange={(e) => setDimensionValue(e.target.value)}>
            {dimensionValues.map((v) => <option key={v}>{v}</option>)}
          </select>
        </label>
      </div>
      {error && <p role="alert">{error}</p>}
      <table className="data-table dense movement-grid">
        <thead>
          <tr>
            <th rowSpan={2}>Month</th>
            <th colSpan={2}>Inbound (IN)</th>
            <th colSpan={2}>Outbound (OUT)</th>
          </tr>
          <tr>
            <th>Quantity</th><th>Unit price</th><th>Quantity</th><th>Unit price</th>
          </tr>
        </thead>
        <tbody>
          {periods.map((p) => (
            <tr key={p}>
              <th scope="row">{formatPeriod(p)}</th>
              <td>{cell(p, 'IN', 'quantity')}</td>
              <td>{cell(p, 'IN', 'unitPrice')}</td>
              <td>{cell(p, 'OUT', 'quantity')}</td>
              <td>{cell(p, 'OUT', 'unitPrice')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Modal>
  );
}
