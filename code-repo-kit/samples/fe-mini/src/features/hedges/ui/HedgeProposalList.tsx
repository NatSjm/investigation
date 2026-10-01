import { useHedgeProposals } from '../api/useHedgeProposals';
export function HedgeProposalList({ clientId }: { clientId: string }) {
  const { data } = useHedgeProposals(clientId);
  return <ul>{data?.map(p => <li key={p.id}>{p.notional}</li>)}</ul>;
}
