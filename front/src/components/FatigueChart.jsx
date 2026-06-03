import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, ReferenceArea, ReferenceLine, Tooltip } from 'recharts'
import { ChartTooltip } from '../utils'

const LEGEND = [
  { color: '#00dbe9', dash: false, label: 'Histórico'    },
  { color: '#00eefc', dash: true,  label: 'Proyección'   },
  { color: '#ffb4ab', dash: true,  label: 'AI Prediction'},
]

export default function FatigueChart({ chartData }) {
  return (
    <div className="glass-card" style={{ borderRadius: 12, padding: 24, height: 400, display: 'flex', flexDirection: 'column' }}>
      {/* Chart header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3 style={{ fontSize: 18, fontWeight: 600, color: '#ffffff', margin: 0 }}>
          Monitoreo de Fatiga &amp; Proyección IA
        </h3>
        <div style={{ display: 'flex', gap: 20 }}>
          {LEGEND.map(({ color, dash, label }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <svg width={24} height={2} style={{ overflow: 'visible' }}>
                <line
                  x1={0} y1={1} x2={24} y2={1}
                  stroke={color} strokeWidth={2}
                  strokeDasharray={dash ? '5 3' : 'none'}
                />
              </svg>
              <span style={{ fontSize: 10, fontFamily: 'JetBrains Mono', color: '#8e9192' }}>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 4, right: 48, left: -20, bottom: 0 }}>
            {/* Zone bands */}
            <ReferenceArea y1={1.5} y2={2.2} fill="#ffb4ab" fillOpacity={0.07} />
            <ReferenceArea y1={1.3} y2={1.5} fill="#facc15" fillOpacity={0.06} />
            <ReferenceArea y1={0.8} y2={1.3} fill="#00eefc" fillOpacity={0.04} />
            <ReferenceArea y1={0}   y2={0.8} fill="#ffb4ab" fillOpacity={0.04} />

            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fill: '#8e9192', fontSize: 10, fontFamily: 'JetBrains Mono' }}
              stroke="rgba(255,255,255,0.08)"
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0.4, 2.0]}
              tick={{ fill: '#8e9192', fontSize: 10, fontFamily: 'JetBrains Mono' }}
              stroke="rgba(255,255,255,0.08)"
            />
            <Tooltip content={<ChartTooltip />} />

            {/* Reference lines for thresholds */}
            <ReferenceLine y={1.5} stroke="#ffb4ab" strokeDasharray="4 3" strokeOpacity={0.5}
              label={{ value: '1.5 ⚠', fill: '#ffb4ab', fontSize: 9, fontFamily: 'JetBrains Mono', position: 'right' }} />
            <ReferenceLine y={1.3} stroke="#facc15" strokeDasharray="4 3" strokeOpacity={0.5}
              label={{ value: '1.3',   fill: '#facc15', fontSize: 9, fontFamily: 'JetBrains Mono', position: 'right' }} />
            <ReferenceLine y={0.8} stroke="#00dbe9" strokeDasharray="4 3" strokeOpacity={0.3}
              label={{ value: '0.8',   fill: '#00dbe9', fontSize: 9, fontFamily: 'JetBrains Mono', position: 'right' }} />

            {/* Data lines */}
            <Line type="monotone" dataKey="acwr_real" name="ACWR Real"
              stroke="#00dbe9" strokeWidth={2.5} dot={false}
              activeDot={{ r: 5, fill: '#00dbe9', stroke: '#080C14', strokeWidth: 2 }}
              connectNulls={false} />
            <Line type="monotone" dataKey="acwr_sim" name="Proyección (Math)"
              stroke="#00eefc" strokeWidth={2} strokeDasharray="7 3" dot={false}
              activeDot={{ r: 4, fill: '#00eefc' }}
              connectNulls={false} />
            <Line type="monotone" dataKey="acwr_ai" name="AI Prediction"
              stroke="#ffb4ab" strokeWidth={2} strokeDasharray="7 3" dot={false}
              activeDot={{ r: 4, fill: '#ffb4ab' }}
              connectNulls={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
