import { RefreshCw, Upload, Users } from 'lucide-react'

export default function Header({ connected, loading, onRefresh, onUploadClick }) {
  return (
    <header
      className="fixed top-0 w-full z-50 flex justify-between items-center px-6 h-16"
      style={{
        background: 'rgba(8,12,20,0.85)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      {/* Left: logo + status */}
      <div className="flex items-center gap-4">
        <span className="text-xl font-bold tracking-tighter text-white">
          SMARTLOAD <span style={{ color: '#00dbe9' }}>|</span> RM
        </span>

        <div
          className="flex items-center gap-1.5 px-3 py-1 rounded-full"
          style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}
        >
          <span
            className={connected ? 'status-pulse' : ''}
            style={{
              display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
              background: connected ? '#00eefc' : '#ffb4ab',
            }}
          />
          <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: '#00dbe9', letterSpacing: '0.1em' }}>
            {connected ? 'API ACTIVA' : 'DESCONECTADO'}
          </span>
        </div>

        <button
          onClick={onRefresh}
          className="p-1.5 rounded-full hover:bg-white/10 transition-colors"
          title="Refrescar datos"
        >
          <RefreshCw size={15} color="#8e9192" className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Right: actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={onUploadClick}
          className="flex items-center gap-2 px-5 py-2 rounded-lg text-sm transition-all active:scale-95"
          style={{
            fontFamily: 'JetBrains Mono',
            color: '#00dbe9',
            border: '1px solid #00dbe9',
            background: 'rgba(0,219,233,0.08)',
          }}
          onMouseEnter={e => (e.currentTarget.style.background = 'rgba(0,219,233,0.16)')}
          onMouseLeave={e => (e.currentTarget.style.background = 'rgba(0,219,233,0.08)')}
        >
          <Upload size={15} />
          Registrar Entrenamiento
        </button>

        <div
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer hover:bg-white/10 transition-colors"
          style={{ border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.05)' }}
        >
          <Users size={18} color="#e5e2e1" />
        </div>
      </div>
    </header>
  )
}
