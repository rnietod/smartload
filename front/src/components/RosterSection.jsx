import { ArrowUpDown } from 'lucide-react'
import { getZone, Sparkline } from '../utils'

export default function RosterSection({ players, selected, onSelect, sparklines, sortByRisk, onToggleSort }) {
  return (
    <section style={{ marginBottom: 32 }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, paddingLeft: 4 }}>
        <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: '#8e9192', letterSpacing: '0.2em', textTransform: 'uppercase' }}>
          Elite Roster Selection
        </span>
        <button
          onClick={onToggleSort}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 12px', borderRadius: 8, fontSize: 11,
            fontFamily: 'JetBrains Mono', cursor: 'pointer',
            color: sortByRisk ? '#00dbe9' : '#8e9192',
            background: sortByRisk ? 'rgba(0,219,233,0.08)' : 'transparent',
            border: sortByRisk ? '1px solid rgba(0,219,233,0.3)' : '1px solid rgba(255,255,255,0.1)',
            transition: 'all 0.2s',
          }}
        >
          <ArrowUpDown size={12} />
          {sortByRisk ? 'Ordenado por Riesgo' : 'Ordenar por Riesgo'}
        </button>
      </div>

      {/* Scrollable cards */}
      <div className="custom-scrollbar" style={{ display: 'flex', gap: 16, overflowX: 'auto', paddingBottom: 12 }}>
        {players.map(player => {
          const isSelected = selected?.player_id === player.player_id
          const zone = getZone(player.acwr_dist)
          const sparkVals = sparklines[player.player_id] || []
          const isDanger = player.color === 'danger'

          return (
            <div
              key={player.player_id}
              onClick={() => onSelect(player)}
              className="glass-card"
              style={{
                flexShrink: 0, width: 240, padding: 16, borderRadius: 12,
                display: 'flex', alignItems: 'center', gap: 14, cursor: 'pointer',
                border: `1px solid ${isSelected ? '#00dbe9' : 'rgba(255,255,255,0.08)'}`,
                background: isSelected ? 'rgba(0,219,233,0.07)' : undefined,
                boxShadow: isSelected ? '0 0 20px rgba(0,219,233,0.12)' : 'none',
              }}
            >
              {/* Avatar + badge */}
              <div style={{ position: 'relative', flexShrink: 0 }}>
                <img
                  src={player.avatar}
                  alt={player.name}
                  style={{
                    width: 56, height: 56, borderRadius: '50%',
                    objectFit: 'cover', objectPosition: 'top',
                    border: `2px solid ${isSelected ? '#00dbe9' : 'rgba(255,255,255,0.12)'}`,
                  }}
                />
                {/* Dorsal */}
                <div style={{
                  position: 'absolute', bottom: -4, right: -4,
                  width: 22, height: 22, borderRadius: '50%',
                  background: isSelected ? '#00dbe9' : '#ffffff',
                  color: '#080C14', fontSize: 9, fontWeight: 700,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  {player.number}
                </div>
                {/* Danger pulse */}
                {isDanger && (
                  <div className="status-pulse" style={{
                    position: 'absolute', top: -2, right: -2,
                    width: 10, height: 10, borderRadius: '50%',
                    background: '#ffb4ab',
                    boxShadow: '0 0 6px rgba(255,180,171,0.8)',
                  }} />
                )}
              </div>

              {/* Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 6, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {player.name}
                </p>
                {/* ACWR badge */}
                <div style={{
                  display: 'inline-flex', alignItems: 'center', gap: 4,
                  padding: '2px 8px', borderRadius: 999, marginBottom: 8,
                  background: `${zone.hex}18`,
                  border: `1px solid ${zone.hex}30`,
                  fontSize: 10, fontFamily: 'JetBrains Mono', color: zone.hex,
                }}>
                  {zone.label !== 'success' && (
                    <span style={{ width: 5, height: 5, borderRadius: '50%', background: zone.hex }} />
                  )}
                  {player.acwr_dist.toFixed(2)} — {zone.label === 'success' ? 'Óptimo' : zone.label === 'warning' ? 'Precaución' : 'Peligro'}
                </div>
                {/* Sparkline */}
                <Sparkline values={sparkVals} color={zone.hex} />
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
