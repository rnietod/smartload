export default function BioCard({ player }) {
  if (!player) return null

  const stats = [
    { label: 'Edad',        value: `${player.age} años`              },
    { label: 'Altura',      value: `${Math.round(player.height)} cm` },
    { label: 'Peso',        value: `${Math.round(player.weight)} kg` },
    { label: 'Nacionalidad',value: player.nationality                },
  ]

  return (
    <div className="glass-card" style={{ borderRadius: 12, overflow: 'hidden' }}>
      {/* Portrait photo with gradient overlay */}
      <div style={{ height: 220, position: 'relative', overflow: 'hidden' }}>
        <img
          src={player.avatar}
          alt={player.name}
          style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top' }}
        />
        {/* Gradient fade */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(to top, #080C14 0%, rgba(8,12,20,0.3) 55%, transparent 100%)',
        }} />
        {/* Name & position */}
        <div style={{ position: 'absolute', bottom: 16, left: 20 }}>
          <h3 style={{ fontSize: 22, fontWeight: 700, color: '#ffffff', margin: 0 }}>
            {player.name}
          </h3>
          <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: '#8e9192', textTransform: 'uppercase', letterSpacing: '0.12em' }}>
            Dorsal {player.number} | {player.position}
          </span>
        </div>
      </div>

      {/* Stats grid */}
      <div style={{ padding: '16px 20px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {stats.map(({ label, value }) => (
          <div key={label} style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: 10, fontFamily: 'JetBrains Mono', color: '#8e9192', marginBottom: 2, textTransform: 'uppercase' }}>
              {label}
            </span>
            <span style={{ fontSize: 15, fontWeight: 500, color: '#e5e2e1', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {value}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
