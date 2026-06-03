import { Download, RefreshCw } from 'lucide-react'
import { getZone, SESSION_TYPES } from '../utils'

export default function WhatIfPlanner({ planDays, simData, onDayChange, onReset, onExport }) {
  return (
    <div className="glass-card" style={{ borderRadius: 12, padding: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
        <div>
          <h3 style={{ fontSize: 18, fontWeight: 600, color: '#ffffff', margin: '0 0 4px 0' }}>
            "What-If" Planner
          </h3>
          <p style={{ fontSize: 13, color: '#8e9192', margin: 0 }}>
            Simula el impacto de las próximas sesiones en el ACWR
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={onExport}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '6px 14px', borderRadius: 8, fontSize: 11,
              fontFamily: 'JetBrains Mono', cursor: 'pointer',
              color: '#00dbe9', background: 'rgba(0,219,233,0.06)',
              border: '1px solid rgba(0,219,233,0.25)', transition: 'all 0.2s',
            }}
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(0,219,233,0.14)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'rgba(0,219,233,0.06)')}
          >
            <Download size={12} /> Exportar Plan
          </button>
          <button
            onClick={onReset}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '6px 14px', borderRadius: 8, fontSize: 11,
              fontFamily: 'JetBrains Mono', cursor: 'pointer',
              color: '#e5e2e1', background: 'transparent',
              border: '1px solid rgba(255,255,255,0.1)', transition: 'all 0.2s',
            }}
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
          >
            <RefreshCw size={12} /> Reiniciar
          </button>
        </div>
      </div>

      {/* Day cards */}
      <div className="custom-scrollbar" style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 8 }}>
        {planDays.map((day, idx) => {
          const simDay   = simData[idx]
          const acwr     = simDay?.math_acwr_dist ?? null
          const zone     = getZone(acwr)
          const isMatch  = day.type === 'Partido'

          return (
            <div
              key={idx}
              style={{
                flexShrink: 0, width: 138, borderRadius: 10, padding: 10,
                display: 'flex', flexDirection: 'column', gap: 8,
                background: 'rgba(13,18,30,0.85)',
                border: `1px solid ${acwr != null ? zone.hex + '35' : 'rgba(255,255,255,0.08)'}`,
              }}
            >
              {/* Day label */}
              <span style={{
                fontSize: 10, fontFamily: 'JetBrains Mono', textAlign: 'center',
                paddingBottom: 8, borderBottom: '1px solid rgba(255,255,255,0.06)',
                color: isMatch ? '#00dbe9' : '#8e9192',
                fontWeight: isMatch ? 700 : 400,
                textTransform: 'uppercase', letterSpacing: '0.06em',
              }}>
                {day.label}
              </span>

              {/* Session type select */}
              <select
                value={day.type}
                onChange={e => onDayChange(day.day_idx, e.target.value)}
                style={{
                  width: '100%', padding: '6px 8px', borderRadius: 6, fontSize: 11,
                  fontFamily: 'JetBrains Mono', color: '#e5e2e1', cursor: 'pointer',
                  background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.1)',
                  outline: 'none', transition: 'border-color 0.2s',
                }}
                onFocus={e => (e.target.style.borderColor = '#00dbe9')}
                onBlur={e => (e.target.style.borderColor = 'rgba(255,255,255,0.1)')}
              >
                {SESSION_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>

              {/* EST. ACWR display */}
              <div style={{
                borderRadius: 6, padding: '8px 4px',
                display: 'flex', flexDirection: 'column', alignItems: 'center',
                background: acwr != null ? `${zone.hex}18` : 'rgba(255,255,255,0.04)',
              }}>
                <span style={{ fontSize: 9, fontFamily: 'JetBrains Mono', color: zone.hex, textTransform: 'uppercase', marginBottom: 4, letterSpacing: '0.06em' }}>
                  EST. ACWR
                </span>
                <span style={{ fontSize: 22, fontWeight: 700, color: zone.hex, letterSpacing: '-0.02em', lineHeight: 1 }}>
                  {acwr != null ? acwr.toFixed(2) : '--'}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
