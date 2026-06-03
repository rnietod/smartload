import { useState } from 'react'
import { LayoutDashboard, Heart, TrendingUp, Calendar, Settings } from 'lucide-react'

const NAV = [
  { icon: LayoutDashboard, label: 'Dashboard',    active: true  },
  { icon: Heart,           label: 'Squad Health', active: false },
  { icon: TrendingUp,      label: 'Performance',  active: false },
  { icon: Calendar,        label: 'Load Planner', active: false },
]

export default function Sidebar() {
  const [expanded, setExpanded] = useState(false)

  return (
    <nav
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
      style={{
        position: 'fixed', left: 0, top: 0, height: '100%', zIndex: 40,
        display: 'flex', flexDirection: 'column',
        width: expanded ? 240 : 72,
        paddingTop: 80, paddingBottom: 24,
        background: 'rgba(8,12,20,0.6)',
        backdropFilter: 'blur(24px)',
        borderRight: '1px solid rgba(255,255,255,0.05)',
        transition: 'width 0.3s cubic-bezier(0.4,0,0.2,1)',
        overflow: 'hidden',
      }}
    >
      {/* Main nav items */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2, padding: '0 8px', flex: 1 }}>
        {NAV.map(({ icon: Icon, label, active }) => (
          <a
            key={label}
            href="#"
            style={{
              display: 'flex', alignItems: 'center', gap: 16,
              padding: '10px 14px', borderRadius: 8,
              color: active ? '#00dbe9' : '#8e9192',
              background: active ? 'rgba(0,219,233,0.06)' : 'transparent',
              borderRight: active ? '2px solid #00dbe9' : '2px solid transparent',
              textDecoration: 'none',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={e => { if (!active) { e.currentTarget.style.color = '#e5e2e1'; e.currentTarget.style.background = 'rgba(255,255,255,0.05)' } }}
            onMouseLeave={e => { if (!active) { e.currentTarget.style.color = '#8e9192'; e.currentTarget.style.background = 'transparent' } }}
          >
            <Icon size={20} style={{ flexShrink: 0 }} />
            <span
              style={{
                fontSize: 13, fontFamily: 'JetBrains Mono',
                opacity: expanded ? 1 : 0,
                transition: 'opacity 0.2s',
              }}
            >
              {label}
            </span>
          </a>
        ))}
      </div>

      {/* Settings at bottom */}
      <div style={{ padding: '0 8px' }}>
        <a
          href="#"
          style={{
            display: 'flex', alignItems: 'center', gap: 16,
            padding: '10px 14px', borderRadius: 8,
            color: '#8e9192', textDecoration: 'none',
            transition: 'all 0.2s', whiteSpace: 'nowrap',
          }}
          onMouseEnter={e => { e.currentTarget.style.color = '#e5e2e1'; e.currentTarget.style.background = 'rgba(255,255,255,0.05)' }}
          onMouseLeave={e => { e.currentTarget.style.color = '#8e9192'; e.currentTarget.style.background = 'transparent' }}
        >
          <Settings size={20} style={{ flexShrink: 0 }} />
          <span style={{ fontSize: 13, fontFamily: 'JetBrains Mono', opacity: expanded ? 1 : 0, transition: 'opacity 0.2s' }}>
            Settings
          </span>
        </a>
      </div>
    </nav>
  )
}
