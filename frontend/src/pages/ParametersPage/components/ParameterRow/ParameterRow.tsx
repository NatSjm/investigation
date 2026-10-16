import { useState } from 'react';
import { formatDateTime } from '@/utils/format';
import type { Parameter, ParameterUpsertRequest } from '@/types/admin';

export interface ParameterRowProps {
  parameter: Parameter;
  pending?: boolean;
  onSave: (key: string, body: ParameterUpsertRequest) => Promise<unknown> | void;
}

const scopeOf = (p: Parameter) => [p.scopeProductGroup, p.scopeCountry, p.scopeValue].filter(Boolean).join(' / ') || 'global';

/** One parameter row with inline value editing (value + valid-from). */
export function ParameterRow({ parameter, pending, onSave }: ParameterRowProps) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(String(parameter.value));
  const [validFrom, setValidFrom] = useState(parameter.validFrom.slice(0, 10));

  const save = async () => {
    const n = Number(value);
    if (Number.isNaN(n)) return;
    await onSave(parameter.key, {
      value: n,
      validFrom,
      scopeProductGroup: parameter.scopeProductGroup,
      scopeCountry: parameter.scopeCountry,
      scopeValue: parameter.scopeValue,
    });
    setEditing(false);
  };

  return (
    <tr className="parameter-row">
      <th scope="row">
        <code>{parameter.key}</code>
      </th>
      <td>{scopeOf(parameter)}</td>
      <td style={{ textAlign: 'right' }}>
        {editing ? (
          <input type="number" step="any" aria-label={`Value of ${parameter.key}`} value={value} onChange={(e) => setValue(e.target.value)} />
        ) : (
          parameter.value
        )}
      </td>
      <td>
        {editing ? (
          <input type="date" aria-label={`Valid from of ${parameter.key}`} value={validFrom} onChange={(e) => setValidFrom(e.target.value)} />
        ) : (
          parameter.validFrom.slice(0, 10)
        )}
      </td>
      <td>
        {parameter.updatedBy} <span className="hint">{formatDateTime(parameter.updatedAt)}</span>
      </td>
      <td>
        {editing ? (
          <>
            <button type="button" className="link" disabled={pending} onClick={save}>
              Save
            </button>
            <button type="button" className="link" onClick={() => setEditing(false)}>
              Cancel
            </button>
          </>
        ) : (
          <button type="button" className="link" onClick={() => setEditing(true)}>
            Edit
          </button>
        )}
      </td>
    </tr>
  );
}
