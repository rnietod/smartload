import { useState, useEffect, useCallback } from 'react'
import { useDisclosure } from '@heroui/react'
import { RefreshCw } from 'lucide-react'

import { getZone, buildPayload, DEFAULT_PLAN } from './utils'
import Header        from './components/Header'
import Sidebar       from './components/Sidebar'
import RosterSection from './components/RosterSection'
import KPIGrid       from './components/KPIGrid'
import BioCard       from './components/BioCard'
import AcwrDisplay   from './components/AcwrDisplay'
import FatigueChart  from './components/FatigueChart'
import WhatIfPlanner from './components/WhatIfPlanner'
import UploadModal   from './components/UploadModal'

export default function App() {
  const [players,      setPlayers]      = useState([])
  const [selected,     setSelected]     = useState(null)
  const [sparklines,   setSparklines]   = useState({})
  const [historyPts,   setHistoryPts]   = useState([])
  const [simData,      setSimData]      = useState([])
  const [chartData,    setChartData]    = useState([])
  const [planDays,     setPlanDays]     = useState(DEFAULT_PLAN)
  const [sortByRisk,   setSortByRisk]   = useState(false)
  const [connected,    setConnected]    = useState(false)
  const [loading,      setLoading]      = useState(true)
  const [uploadFile,   setUploadFile]   = useState(null)
  const [uploadStatus, setUploadStatus] = useState(null)
  const { isOpen, onOpen, onClose }     = useDisclosure()

  // ── Fetch all players + sparklines
  const fetchPlayers = useCallback(async () => {
    setLoading(true)
    try {
      const res  = await fetch('/api/players')
      if (!res.ok) throw new Error()
      const data = await res.json()
      setPlayers(data)
      setConnected(true)
      setSelected(prev => prev ?? data[0] ?? null)

      const results = await Promise.all(
        data.map(p =>
          fetch(`/api/players/${p.player_id}/history`)
            .then(r => r.json())
            .then(h => ({ id: p.player_id, values: h.history.slice(-7).map(d => d.acwr_dist) }))
            .catch(() => ({ id: p.player_id, values: [] }))
        )
      )
      const map = {}
      results.forEach(({ id, values }) => { map[id] = values })
      setSparklines(map)
    } catch {
      setConnected(false)
    } finally {
      setLoading(false)
    }
  }, [])

  // ── Fetch 15-day history for selected player
  const fetchHistory = useCallback(async (pid) => {
    try {
      const res  = await fetch(`/api/players/${pid}/history`)
      if (!res.ok) throw new Error()
      const data = await res.json()
      setHistoryPts(data.history.slice(-15))
    } catch { setHistoryPts([]) }
  }, [])

  // ── Run simulation
  const runSim = useCallback(async (pid, plan) => {
    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPayload(pid, plan)),
      })
      if (!res.ok) throw new Error()
      const data = await res.json()
      setSimData(data.trajectory || [])
    } catch { setSimData([]) }
  }, [])

  // ── Effects
  useEffect(() => { fetchPlayers() }, [fetchPlayers])

  useEffect(() => {
    if (!selected) return
    fetchHistory(selected.player_id)
    runSim(selected.player_id, planDays)
  }, [selected?.player_id])

  useEffect(() => {
    if (selected) runSim(selected.player_id, planDays)
  }, [planDays])

  // ── Merge chart data
  useEffect(() => {
    const hist = historyPts.map((d, i) => {
      const isToday = i === historyPts.length - 1
      return {
        label:     isToday ? 'Hoy' : `D-${historyPts.length - 1 - i}`,
        acwr_real: d.acwr_dist,
        acwr_sim:  isToday ? d.acwr_dist : undefined,
        acwr_ai:   isToday ? d.acwr_dist : undefined,
      }
    })
    const sim = simData.slice(0, 15).map((d, i) => ({
      label:     i < planDays.length ? planDays[i].label : `D+${i + 1}`,
      acwr_real: undefined,
      acwr_sim:  d.math_acwr_dist,
      acwr_ai:   d.predicted_acwr_dist,
    }))
    setChartData([...hist, ...sim])
  }, [historyPts, simData, planDays])

  // ── Handlers
  const handlePlanChange = (dayIdx, newType) =>
    setPlanDays(prev => prev.map(d => d.day_idx === dayIdx ? { ...d, type: newType } : d))

  const exportPlan = () => {
    const rows = ['Día,Tipo,ACWR Estimado',
      ...planDays.map((d, i) => {
        const v = simData[i]?.math_acwr_dist
        return `${d.label},${d.type},${v != null ? v.toFixed(2) : '--'}`
      })
    ].join('\n')
    const a = Object.assign(document.createElement('a'), {
      href: URL.createObjectURL(new Blob([rows], { type: 'text/csv' })),
      download: `plan_${selected?.name?.split(' ')[0] || 'jugador'}.csv`,
    })
    a.click()
  }

  // ── KPIs
  const kpis = {
    total:   players.length,
    fitness: players.length ? Math.round((players.filter(p => p.color === 'success').length / players.length) * 100) : 0,
    fatigue: players.filter(p => p.color === 'warning').length,
    danger:  players.filter(p => p.color === 'danger').length,
  }

  const sortedPlayers = sortByRisk
    ? [...players].sort((a, b) => ({ danger: 0, warning: 1, success: 2 }[a.color] ?? 3) - ({ danger: 0, warning: 1, success: 2 }[b.color] ?? 3))
    : players

  // ── Loading screen
  if (loading && players.length === 0) {
    return (
      <div style={{ minHeight: '100vh', background: '#080C14', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16 }}>
        <RefreshCw size={32} color="#00dbe9" className="animate-spin" />
        <p style={{ color: '#8e9192', fontFamily: 'JetBrains Mono', fontSize: 13 }}>Conectando con SmartLoad API...</p>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#080C14', color: '#e5e2e1', fontFamily: 'Geist, sans-serif' }}>
      <Header
        connected={connected}
        loading={loading}
        onRefresh={fetchPlayers}
        onUploadClick={onOpen}
      />

      <Sidebar />

      <main style={{ marginLeft: 72, paddingTop: 88, paddingLeft: 24, paddingRight: 24, paddingBottom: 40 }}>
        <RosterSection
          players={sortedPlayers}
          selected={selected}
          onSelect={setSelected}
          sparklines={sparklines}
          sortByRisk={sortByRisk}
          onToggleSort={() => setSortByRisk(v => !v)}
        />

        <KPIGrid kpis={kpis} />

        {selected && (
          <div style={{ display: 'grid', gridTemplateColumns: '4fr 8fr', gap: 20 }}>
            {/* Left column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <BioCard player={selected} />
              <AcwrDisplay player={selected} />
            </div>

            {/* Right column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <FatigueChart chartData={chartData} />
              <WhatIfPlanner
                planDays={planDays}
                simData={simData}
                onDayChange={handlePlanChange}
                onReset={() => setPlanDays(DEFAULT_PLAN)}
                onExport={exportPlan}
              />
            </div>
          </div>
        )}
      </main>

      <UploadModal
        isOpen={isOpen}
        onClose={onClose}
        uploadFile={uploadFile}
        setUploadFile={setUploadFile}
        uploadStatus={uploadStatus}
        onUpload={() => {
          setUploadStatus('loading')
          setTimeout(() => setUploadStatus('success'), 1500)
        }}
      />
    </div>
  )
}
