// ─── ZONE COLORS ─────────────────────────────────────────────────────────────
export function getZone(acwr) {
  if (acwr == null) return { hex: '#8e9192', label: 'unknown', text: '#8e9192' }
  if (acwr < 0.8 || acwr > 1.5) return { hex: '#ffb4ab', label: 'danger',  text: '#ffb4ab' }
  if (acwr > 1.3)                return { hex: '#facc15', label: 'warning', text: '#facc15' }
  return                                { hex: '#00eefc', label: 'success', text: '#00eefc' }
}

// ─── SESSION PRESETS ──────────────────────────────────────────────────────────
export const SESSION_PRESETS = {
  'Descanso':  { total_distance: 0,     acc_band7plus_total_effort_count: 0,  velocity_band6plus7_total_distance: 0,    is_official_match: 0 },
  'Ligera':    { total_distance: 4000,  acc_band7plus_total_effort_count: 5,  velocity_band6plus7_total_distance: 100,  is_official_match: 0 },
  'Normal':    { total_distance: 7000,  acc_band7plus_total_effort_count: 15, velocity_band6plus7_total_distance: 400,  is_official_match: 0 },
  'Alta Int.': { total_distance: 10000, acc_band7plus_total_effort_count: 35, velocity_band6plus7_total_distance: 900,  is_official_match: 0 },
  'Partido':   { total_distance: 11000, acc_band7plus_total_effort_count: 45, velocity_band6plus7_total_distance: 1200, is_official_match: 1 },
}

export const SESSION_TYPES = ['Descanso', 'Ligera', 'Normal', 'Alta Int.', 'Partido']

// ─── DEFAULT PLAN ─────────────────────────────────────────────────────────────
export const DEFAULT_PLAN = [
  { day_idx: 0, label: 'D-2',       type: 'Ligera'    },
  { day_idx: 1, label: 'D-1',       type: 'Descanso'  },
  { day_idx: 2, label: 'Partido',   type: 'Partido'   },
  { day_idx: 3, label: 'D+1',       type: 'Normal'    },
  { day_idx: 4, label: 'D+2',       type: 'Alta Int.' },
  { day_idx: 5, label: 'D+3',       type: 'Ligera'    },
  { day_idx: 6, label: 'Partido 2', type: 'Partido'   },
]

// ─── BUILD SIMULATION PAYLOAD ─────────────────────────────────────────────────
export function buildPayload(playerId, planDays) {
  const plan = planDays.map(d => ({
    day_idx: d.day_idx,
    type: d.type,
    ...SESSION_PRESETS[d.type],
  }))
  while (plan.length < 15) {
    plan.push({ day_idx: plan.length, type: 'Normal', ...SESSION_PRESETS['Normal'] })
  }
  return { player_id: playerId, plan }
}

// ─── SPARKLINE SVG ────────────────────────────────────────────────────────────
export function Sparkline({ values, color }) {
  if (!values || values.length < 2) return <div style={{ height: 20, width: 64 }} />
  const W = 64, H = 20
  const min = Math.min(...values)
  const max = Math.max(...values)
  const rng = (max - min) || 0.1
  const pts = values
    .map((v, i) => `${(i / (values.length - 1)) * W},${H - ((v - min) / rng) * (H - 4) - 2}`)
    .join(' ')
  return (
    <svg width={W} height={H} style={{ overflow: 'visible', display: 'block' }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

// ─── RECHARTS TOOLTIP ─────────────────────────────────────────────────────────
export function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'rgba(8,12,20,0.95)',
      border: '1px solid rgba(255,255,255,0.12)',
      borderRadius: 8, padding: '10px 14px',
      fontFamily: 'JetBrains Mono', fontSize: 11,
    }}>
      <p style={{ color: '#8e9192', marginBottom: 6 }}>{label}</p>
      {payload.map((e, i) => (
        <p key={i} style={{ color: e.color, margin: '2px 0' }}>
          {e.name}: <strong>{typeof e.value === 'number' ? e.value.toFixed(3) : e.value}</strong>
        </p>
      ))}
    </div>
  )
}
