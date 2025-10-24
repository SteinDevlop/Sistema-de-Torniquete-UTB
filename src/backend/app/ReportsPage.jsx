import React, { useMemo } from 'react'
import accessesData from '../data/accesses.json'

export default function ReportsPage() {
  // For demo use localStorage accesses or fallback
  const accesses = JSON.parse(localStorage.getItem('st_accesses')) || accessesData

  const totalByDay = useMemo(() => {
    const map = {}
    accesses.forEach(a => {
      const day = new Date(a.datetime).toISOString().split('T')[0]
      map[day] = (map[day] || 0) + 1
    })
    return Object.entries(map).sort()
  }, [accesses])

  const allowedDenied = useMemo(() => {
    let p = 0, d = 0
    accesses.forEach(a => a.result === 'Permitido' ? p++ : d++)
    return { p, d }
  }, [accesses])

  const topUsers = useMemo(() => {
    const map = {}
    accesses.forEach(a => { map[a.name] = (map[a.name] || 0) + 1 })
    return Object.entries(map).sort((a, b) => b[1] - a[1]).slice(0, 5)
  }, [accesses])

  function exportCSV() {
    const rows = [['Tipo', 'Valor'], ['Permitidos', allowedDenied.p], ['Denegados', allowedDenied.d]]
    const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'report_summary.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Reportes</h2>
        <div>
          <button onClick={exportCSV} className="px-3 py-1 bg-utb text-white rounded">Exportar resumen</button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 border rounded">
          <h3 className="font-semibold mb-2">Total de accesos por día</h3>
          <ul className="text-sm space-y-1">
            {totalByDay.map(([day, v]) => <li key={day} className="flex justify-between"><span>{day}</span><span className="font-medium">{v}</span></li>)}
            {totalByDay.length === 0 && <li className="text-gray-500">Sin datos</li>}
          </ul>
        </div>

        <div className="bg-white p-4 border rounded">
          <h3 className="font-semibold mb-2">Permitidos vs Denegados</h3>
          <div className="flex gap-2 items-center">
            <div className="w-2/3">
              <div className="h-6 bg-green-200" style={{ width: `${allowedDenied.p + allowedDenied.d ? (allowedDenied.p / (allowedDenied.p + allowedDenied.d) * 100) : 50}%` }}></div>
              <div className="h-6 bg-red-200" style={{ width: `${allowedDenied.p + allowedDenied.d ? (allowedDenied.d / (allowedDenied.p + allowedDenied.d) * 100) : 50}%`, marginTop: 6 }}></div>
            </div>
            <div className="text-sm">
              <div><strong className="text-green-600">{allowedDenied.p}</strong> Permitidos</div>
              <div><strong className="text-red-600">{allowedDenied.d}</strong> Denegados</div>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 border rounded">
          <h3 className="font-semibold mb-2">Usuarios más frecuentes</h3>
          <ol className="text-sm list-decimal list-inside">
            {topUsers.map(([name, cnt]) => <li key={name}>{name} — {cnt}</li>)}
            {topUsers.length === 0 && <li className="text-gray-500">Sin datos</li>}
          </ol>
        </div>
      </div>
    </div>
  )
}