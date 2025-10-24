import React, { useEffect, useState } from 'react'
import Header from '../components/Header'
import UserCard from '../components/UserCard'
import AccessTable from '../components/AccessTable'
import usersData from '../data/users.json'
import accessesData from '../data/accesses.json'

export default function OperatorView({ user, onLogout }) {
  const [code, setCode] = useState('')
  const [current, setCurrent] = useState(null)
  const [status, setStatus] = useState('idle') // idle, allowed, denied, waiting
  const [recent, setRecent] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('st_accesses')) || accessesData
    } catch {
      return accessesData
    }
  })

  useEffect(() => {
    localStorage.setItem('st_accesses', JSON.stringify(recent))
  }, [recent])

  function simulateVerify() {
    setStatus('waiting')
    const codeTrim = code.trim()
    setTimeout(() => {
      const found = usersData.find(u => u.id.toLowerCase() === codeTrim.toLowerCase())
      if (!found) {
        const record = {
          userId: codeTrim || 'DESCONOCIDO',
          name: 'Usuario no encontrado',
          role: '-',
          datetime: new Date().toISOString(),
          result: 'Denegado'
        }
        setStatus('denied')
        setCurrent(null)
        setRecent(prev => [record, ...prev].slice(0, 50))
        return
      }

      const allowed = found.status === 'Activo'
      const record = {
        userId: found.id,
        name: found.name,
        role: found.role,
        datetime: new Date().toISOString(),
        result: allowed ? 'Permitido' : 'Denegado'
      }
      setCurrent(found)
      setStatus(allowed ? 'allowed' : 'denied')
      setRecent(prev => [record, ...prev].slice(0, 50))
    }, 900)
  }

  function statusColor() {
    if (status === 'waiting') return 'bg-yellow-400'
    if (status === 'allowed') return 'bg-green-500'
    if (status === 'denied') return 'bg-red-500'
    return 'bg-gray-200'
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="Sistema de Torniquete UTB – Módulo Operador" userName={user.name} onLogout={onLogout} />
      <main className="p-6 bg-gray-50 flex-1">
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
          <section className="md:col-span-2 space-y-4">
            <div className="bg-white p-4 border rounded">
              <label className="block text-sm font-medium text-gray-700 mb-2">Ingrese código o escanee el carnet</label>
              <div className="flex gap-2">
                <input value={code} onChange={e => setCode(e.target.value)} placeholder="Ingrese código o escanee el carnet" className="flex-1 border rounded px-3 py-2" />
                <button onClick={simulateVerify} className="bg-utb text-white px-4 py-2 rounded">Verificar acceso</button>
              </div>
              <div className="mt-4 flex items-center gap-4">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white ${statusColor()} font-bold`}>
                  {status === 'waiting' ? '...' : status === 'allowed' ? '✓' : status === 'denied' ? '✕' : '?'}
                </div>
                <div>
                  <div className="text-sm text-gray-600">Indicador del torniquete</div>
                  <div className="text-sm text-gray-800 uppercase">{status === 'waiting' ? 'En espera' : status === 'allowed' ? 'Acceso permitido' : status === 'denied' ? 'Acceso denegado' : 'Sin estado'}</div>
                </div>
              </div>
            </div>

            <div className="bg-white p-4 border rounded">
              <h3 className="text-lg font-semibold mb-3">Panel de información del usuario</h3>
              <UserCard user={current ? {
                id: current.id,
                name: current.name,
                role: current.role,
                status: current.status,
                last_access: current.last_access
              } : null} />
            </div>
          </section>

          <aside className="space-y-4">
            <div className="bg-white p-4 border rounded">
              <h3 className="text-md font-semibold mb-2">Registro rápido (últimos 10)</h3>
              <AccessTable items={recent} max={10} />
            </div>

            <div className="bg-white p-4 border rounded text-xs text-gray-500">
              Demo: datos simulados. La información proviene de JSON local y se guarda en localStorage.
            </div>
          </aside>
        </div>
      </main>
    </div>
  )
}