import { AlertTriangle, CheckCircle } from 'lucide-react'
import { getZone } from '../utils'

export default function AcwrDisplay({ player }) {
  if (!player) return null
  const zone = getZone(player.acwr_dist)

  const message =
    zone.label === 'danger'
      ? 'Nivel crítico. Alto riesgo de lesión. Reducir volumen inmediatamente.'
      : zone.label === 'warning'
      ? `Carga ${Math.abs(Math.round((player.acwr_dist - 1) * 100))}% por encima de la media histórica. Se recomienda reducción de volumen.`
      : 'Carga en parámetros óptimos. Riesgo de lesión minimizado.'

  return (
    <div
      className="glass-card"
      style={{
        padding: 24, borderRadius: 12,
        display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
        background: `rgba(${zone.label === 'danger' ? '255,180,171' : zone.label === 'warning' ? '234,179,8' : '0,238,252'},0.04)`,
        border: `1px solid ${zone.hex}25`,
      }}
    >
      {/* Title */}
      <span style={{ fontSize: 10, fontFamily: 'JetBrains Mono', color: '#8e9192', textTransform: 'uppercase', letterSpacing: '0.2em', marginBottom: 12 }}>
        Acute:Chronic Workload Ratio
      </span>

      {/* Big ACWR number */}
      <div style={{
        fontSize: 72, fontWeight: 700, lineHeight: 1,
        color: zone.hex, letterSpacing: '-0.04em',
        marginBottom: 16,
        textShadow: `0 0 40px ${zone.hex}60`,
      }}>
        {player.acwr_dist.toFixed(2)}
      </div>

      {/* Zone badge */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '6px 16px', borderRadius: 999, marginBottom: 16,
        background: `${zone.hex}18`, border: `1px solid ${zone.hex}35`,
      }}>
        {zone.label === 'success'
          ? <CheckCircle size={14} color={zone.hex} />
          : <AlertTriangle size={14} color={zone.hex} />
        }
        <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: zone.hex, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          {player.zone}
        </span>
      </div>

      {/* Description */}
      <p style={{ fontSize: 13, color: '#8e9192', lineHeight: 1.6, marginBottom: 20 }}>
        {message}
      </p>

      {/* Acute / Chronic sub-stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, width: '100%' }}>
        {[
          { label: 'CARGA AGUDA',   value: `${Math.round(player.acute_dist)}m`   },
          { label: 'CARGA CRÓNICA', value: `${Math.round(player.chronic_dist)}m` },
        ].map(({ label, value }) => (
          <div key={label} style={{ padding: 12, borderRadius: 8, background: 'rgba(255,255,255,0.04)', textAlign: 'center' }}>
            <p style={{ fontSize: 9, fontFamily: 'JetBrains Mono', color: '#8e9192', textTransform: 'uppercase', marginBottom: 4 }}>{label}</p>
            <p style={{ fontSize: 20, fontWeight: 700, color: '#e5e2e1', letterSpacing: '-0.02em' }}>{value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
