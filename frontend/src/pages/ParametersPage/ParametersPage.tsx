import { useState } from 'react';
import { useParameters, useUpsertParameter } from '@/pages/ParametersPage/hook/useParameters';
import { ParameterRow } from '@/pages/ParametersPage/components/ParameterRow';
import type { ProductGroup } from '@/types/admin';

/** `/admin/parameters` - parameter sets with product group filter and inline editing.
 * @docs ADM-001
 */
export function ParametersPage() {
  const [productGroup, setProductGroup] = useState<ProductGroup | undefined>(undefined);
  const { data, isLoading, error } = useParameters(productGroup);
  const upsert = useUpsertParameter();

  return (
    <section className="page admin-parameters">
      <header className="toolbar">
        <h1>Parameters</h1>
        <label>
          Product group
          <select value={productGroup ?? ''} onChange={(e) => setProductGroup((e.target.value || undefined) as ProductGroup | undefined)}>
            <option value="">All</option>
            <option value="product1">Product 1</option>
            <option value="product2">Product 2</option>
          </select>
        </label>
      </header>
      {isLoading && <p>Loading parameters...</p>}
      {error && <p role="alert">Parameters could not be loaded.</p>}
      {upsert.error && <p role="alert">The parameter could not be saved.</p>}
      <table className="data-table">
        <thead>
          <tr>
            <th scope="col">Key</th>
            <th scope="col">Scope</th>
            <th scope="col" style={{ textAlign: 'right' }}>
              Value
            </th>
            <th scope="col">Valid from</th>
            <th scope="col">Updated</th>
            <th scope="col" />
          </tr>
        </thead>
        <tbody>
          {(data ?? []).map((p) => (
            <ParameterRow
              key={`${p.key}|${p.scopeProductGroup ?? ''}|${p.scopeCountry ?? ''}|${p.scopeValue ?? ''}`}
              parameter={p}
              pending={upsert.isPending}
              onSave={(key, body) => upsert.mutateAsync({ key, body })}
            />
          ))}
          {data?.length === 0 && (
            <tr>
              <td colSpan={6} className="empty">
                No parameters
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
