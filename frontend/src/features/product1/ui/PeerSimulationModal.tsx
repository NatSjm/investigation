import { useState } from 'react';
import { LineChart } from '@/shared/charts/LineChart';
import { Modal } from '@/shared/ui/Modal';
import { formatQty } from '@/shared/utils/format';
import { formatPeriod } from '@/shared/utils/months';
import type { PeerSimulationRequest, PeerSimulationResult } from '../product1.types';

export interface PeerSimulationModalProps {
  open: boolean;
  onClose: () => void;
  segments: readonly string[];
  result?: PeerSimulationResult;
  pending?: boolean;
  onSubmit: (request: PeerSimulationRequest) => Promise<unknown> | void;
}

/**
 * Modal 2: movements of similar products at peer firms. Picks a peer segment and a scaling
 * factor (default `peer.scaling_default` = 1.0) and shows the simulated monthly series.
 */
export function PeerSimulationModal({ open, onClose, segments, result, pending, onSubmit }: PeerSimulationModalProps) {
  const [peerSegment, setPeerSegment] = useState<string>(segments[0] ?? '');
  const [scalingFactor, setScalingFactor] = useState('1.0');

  const factor = Number(scalingFactor);
  const valid = peerSegment !== '' && factor > 0 && factor <= 5;

  return (
    <Modal
      open={open}
      title="Peer simulation"
      onClose={onClose}
      width={720}
      footer={
        <>
          <button type="button" onClick={onClose}>
            Close
          </button>
          <button type="button" className="primary" disabled={!valid || pending} onClick={() => onSubmit({ peerSegment, scalingFactor: factor })}>
            Run simulation
          </button>
        </>
      }
    >
      <div className="modal-controls">
        <label>
          Peer segment
          <select value={peerSegment} onChange={(e) => setPeerSegment(e.target.value)}>
            {segments.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>
        <label>
          Scaling factor (0 - 5)
          <input type="number" min={0.1} max={5} step={0.1} value={scalingFactor} onChange={(e) => setScalingFactor(e.target.value)} />
        </label>
      </div>
      {result ? (
        <figure>
          <figcaption>
            Segment median x {result.scalingFactor} - {result.peerSegment}
          </figcaption>
          <LineChart
            data={result.series.map((p) => ({ period: p.period, value: p.value }))}
            series={[{ key: 'value', label: 'Peer quantity' }]}
            yFormatter={formatQty}
            xFormatter={(p) => formatPeriod(p, 'short')}
            height={220}
          />
        </figure>
      ) : (
        <p className="hint">Run the simulation to see the peer series.</p>
      )}
    </Modal>
  );
}
