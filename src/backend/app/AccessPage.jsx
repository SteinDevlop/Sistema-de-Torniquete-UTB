import React, { useEffect, useMemo, useState } from 'react'
import accessesJson from '../data/accesses.json'

export default function AccessPage() {
  const [accesses, setAccesses] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('st_accesses')) || accessesJson
    } catch {
      return accessesJson
    }
  })
  const [filter, setFilter] = useState({ query: '', result: 'Todos', from: '', to: '' })

  useEffect(() => {
    localStorage.setItem('st_accesses', JSON.stringify(accesses))
  }, [accesses])

  const filtered = useMemo(() => {
    return accesses.filter(a => {
      if (filter.result !== 'Todos' && a.result !== filter.result) return false
      if (filter.query && !(`${a.name} ${a.userId}`.toLowerCase().includes(filter.query.toLowerCase()))) return false
      if (filter.from && new Date(a.datetime) < new Date(filter.from)) return false
      if (filter.to && new Date(a.datetime) > new Date(filter.to)) return false
      return true
    })
  }, [accesses, filter])

  function exportCSV() {
    const rows = [['ID Usuario', 'Nombre', 'Tipo', 'Fecha', 'Resultado'], ...filtered.map(r => [r.userId, r.name, r.role, new Date(r.datetime).toLocaleString(), r.result])]
    const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'accesos.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Registros de accesos</h2>
        <div className="flex gap-2">
          <button onClick={exportCSV} className="px-3 py-1 bg-utb text-white rounded">Exportar CSV</button>
        </div>
      </div>

      <div className="bg-white p-4 border rounded mb-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input value={filter.query} onChange={e => setFilter(f => ({ ...f, query: e.target.value }))} placeholder="Buscar por nombre o ID" className="border rounded px-2 py-1" />
          <select value={filter.result} onChange={e => setFilter(f => ({ ...f, result: e.target.value }))} className="border rounded px-2 py-1">
            <option>Todos</option>
            <option>Permitido</option>
            <option>Denegado</option>
          </select>
          <input type="date" value={filter.from} onChange={e => setFilter(f => ({ ...f, from: e.target.value }))} className="border rounded px-2 py-1" />
          <input type="date" value={filter.to} onChange={e => setFilter(f => ({ ...f, to: e.target.value }))} className="border rounded px-2 py-1" />
        </div>
      </div>

      <div className="bg-white border rounded overflow-auto">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2">ID Usuario</th>
              <th className="px-4 py-2">Nombre</th>
              <th className="px-4 py-2">Tipo</th>
              <th className="px-4 py-2">Fecha</th>
              <th className="px-4 py-2">Resultado</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r, i) => (
              <tr key={i} className="odd:bg-white even:bg-gray-50">
                <td className="px-4 py-2">{r.userId}</td>
                <td className="px-4 py-2">{r.name}</td>
                <td className="px-4 py-2">{r.role}</td>
                <td className="px-4 py-2">{new Date(r.datetime).toLocaleString()}</td>
                <td className={`px-4 py-2 font-semibold ${r.result === 'Permitido' ? 'text-green-600' : 'text-red-600'}`}>{r.result}</td>
              </tr>
            ))}
            {filtered.length === 0 && <tr><td colSpan="5" className="p-6 text-center text-gray-500">No hay registros</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}