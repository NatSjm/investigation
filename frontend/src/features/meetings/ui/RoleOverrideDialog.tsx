import { useState } from 'react';
import { Modal } from '@/shared/ui/Modal';
import { useRoleOverride } from '../api/useRoleOverride';
import type { ClientRole } from '../meetings.types';

export interface RoleOverrideDialogProps {
  open: boolean;
  sessionId: string;
  currentRole?: ClientRole;
  onClose: () => void;
}

const ROLES: Array<{ value: ClientRole; label: string }> = [
  { value: 'IMPORTER', label: 'Importer' },
  { value: 'EXPORTER', label: 'Exporter' },
  { value: 'MIXED', label: 'Mixed' },
];

/** Manual role override with mandatory reason (replaces the algorithm result for this session). */
export function RoleOverrideDialog({ open, sessionId, currentRole, onClose }: RoleOverrideDialogProps) {
  const [role, setRole] = useState<ClientRole>(currentRole ?? 'MIXED');
  const [reason, setReason] = useState('');
  const override = useRoleOverride(sessionId);

  const submit = async () => {
    if (reason.trim().length < 5) return;
    await override.mutateAsync({ role, reason: reason.trim() });
    setReason('');
    onClose();
  };

  return (
    <Modal
      open={open}
      title="Override client role"
      onClose={onClose}
      width={480}
      footer={
        <>
          <button type="button" onClick={onClose}>
            Cancel
          </button>
          <button type="button" className="primary" disabled={override.isPending || reason.trim().length < 5} onClick={submit}>
            Apply override
          </button>
        </>
      }
    >
      <fieldset>
        <legend>Role for this session</legend>
        {ROLES.map((r) => (
          <label key={r.value} className="radio">
            <input type="radio" name="role" value={r.value} checked={role === r.value} onChange={() => setRole(r.value)} />
            {r.label}
          </label>
        ))}
      </fieldset>
      <label>
        Reason (required)
        <textarea rows={3} value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Why the algorithm result does not apply" />
      </label>
      {override.error && <p role="alert">The override could not be saved.</p>}
    </Modal>
  );
}
