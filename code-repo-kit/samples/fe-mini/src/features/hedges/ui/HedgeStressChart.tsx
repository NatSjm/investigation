export function HedgeStressChart({ series }: { series: number[] }) {
  return <svg>{series.map((v, i) => <rect key={i} height={v} />)}</svg>;
}
