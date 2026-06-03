import { useRef } from 'react'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button } from '@heroui/react'
import { Upload, CheckCircle } from 'lucide-react'

const REQUIRED_COLS = ['player_id', 'date', 'total_distance', 'acc_band7plus', 'velocity_band6plus7', 'is_official_match']

export default function UploadModal({ isOpen, onClose, uploadFile, setUploadFile, uploadStatus, onUpload }) {
  const fileRef = useRef(null)

  const handleClose = () => {
    setUploadFile(null)
    onClose()
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      backdrop="blur"
      size="md"
      classNames={{
        base:   'bg-[#0d121e] border border-white/10',
        header: 'border-b border-white/10',
        footer: 'border-t border-white/10',
      }}
    >
      <ModalContent>
        <ModalHeader style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <span style={{ color: '#ffffff', fontWeight: 600 }}>Importar Sesiones de Entrenamiento</span>
          <span style={{ fontSize: 12, color: '#8e9192', fontFamily: 'JetBrains Mono', fontWeight: 400 }}>
            Carga un archivo CSV o Excel con datos de sesiones
          </span>
        </ModalHeader>

        <ModalBody>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Drop zone */}
            <div
              onClick={() => fileRef.current?.click()}
              style={{
                borderRadius: 12, padding: '32px 16px',
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
                cursor: 'pointer', transition: 'all 0.2s',
                border: `2px dashed ${uploadFile ? '#00dbe9' : 'rgba(0,219,233,0.3)'}`,
                background: uploadFile ? 'rgba(0,219,233,0.06)' : 'rgba(0,219,233,0.02)',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(0,219,233,0.08)')}
              onMouseLeave={e => (e.currentTarget.style.background = uploadFile ? 'rgba(0,219,233,0.06)' : 'rgba(0,219,233,0.02)')}
            >
              <Upload size={36} color="#00dbe9" />
              <p style={{ color: '#e5e2e1', fontSize: 14, fontWeight: 500, textAlign: 'center', margin: 0 }}>
                {uploadFile ? uploadFile.name : 'Arrastra tu archivo o haz clic para seleccionar'}
              </p>
              <p style={{ color: '#8e9192', fontSize: 11, fontFamily: 'JetBrains Mono', margin: 0 }}>
                CSV · XLSX · XLS — Máx. 50 MB
              </p>
              <input
                ref={fileRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                style={{ display: 'none' }}
                onChange={e => setUploadFile(e.target.files?.[0] || null)}
              />
            </div>

            {/* Required columns */}
            <div style={{ borderRadius: 8, padding: 12, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
              <p style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: '#8e9192', marginBottom: 8 }}>Columnas requeridas:</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {REQUIRED_COLS.map(col => (
                  <span key={col} style={{
                    padding: '2px 8px', borderRadius: 4, fontSize: 10,
                    fontFamily: 'JetBrains Mono', color: '#00dbe9',
                    background: 'rgba(0,219,233,0.1)', border: '1px solid rgba(0,219,233,0.2)',
                  }}>
                    {col}
                  </span>
                ))}
              </div>
            </div>

            {/* Success message */}
            {uploadStatus === 'success' && (
              <div style={{
                borderRadius: 8, padding: '10px 14px',
                display: 'flex', alignItems: 'center', gap: 10,
                background: 'rgba(0,238,252,0.08)', border: '1px solid rgba(0,238,252,0.25)',
              }}>
                <CheckCircle size={16} color="#00eefc" />
                <span style={{ fontSize: 12, color: '#00eefc', fontFamily: 'JetBrains Mono' }}>
                  Demo: 24 sesiones importadas de 6 jugadores ✓
                </span>
              </div>
            )}
          </div>
        </ModalBody>

        <ModalFooter>
          <Button variant="light" onPress={handleClose} style={{ color: '#8e9192' }}>
            Cancelar
          </Button>
          <Button
            isDisabled={!uploadFile}
            onPress={onUpload}
            style={{
              background: uploadFile ? '#00dbe9' : 'rgba(0,219,233,0.2)',
              color: uploadFile ? '#080C14' : '#00dbe9',
              fontFamily: 'JetBrains Mono', fontSize: 13,
            }}
          >
            {uploadStatus === 'success' ? '✓ Importado' : 'Importar Sesiones'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
