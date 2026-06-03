const KPIS = [
  { key: 'total',   label: 'Total Plantilla',   sub: 'Atletas activos',    color: '#e5e2e1' },
  { key: 'fitness', label: 'Tasa de Fitness',   sub: 'Estado Óptimo',      color: '#00eefc', suffix: '%' },
  { key: 'fatigue', label: 'Alertas de Fatiga', sub: 'En observación',     color: '#facc15' },
  { key: 'danger',  label: 'Riesgo Alto',        sub: 'Riesgo inminente',   color: '#ffb4ab' },
]

export default function KPIGrid({ kpis }) {
  return (
    <section
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 20,
        marginBottom: 32,
      }}
    >
      {KPIS.map(({ key, label, sub, color, suffix = '' }) => (
        <div
          key={key}
          className="glass-card"
          style={{ padding: 24, borderRadius: 12, display: 'flex', flexDirection: 'column', gap: 4 }}
        >
          <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: '#8e9192' }}>
            {label}
          </span>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, marginTop: 4 }}>
            <span style={{ fontSize: 36, fontWeight: 700, color, letterSpacing: '-0.04em', lineHeight: 1 }}>
              {kpis[key]}{suffix}
            </span>
            <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color, paddingBottom: 4 }}>
              {sub}
            </span>
          </div>
        </div>
      ))}
    </section>
  )
}
