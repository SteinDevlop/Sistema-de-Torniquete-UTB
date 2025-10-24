import React from 'react'

export default function AccessTable({ items = [], max = 10 }) {
  const rows = items.slice(0, max)
  return (
    <div className="overflow-auto bg-white border rounded">
      <table className="min-w-full">
        <thead className="bg-gray-50 text-left">
          <tr>
            <th className="px-4 py-2 text-sm">Nombre</th>
            <th className="px-4 py-2 text-sm">Tipo</th>
            <th className="px-4 py-2 text-sm">Fecha</th>
            <th className="px-4 py-2 text-sm">Resultado</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="odd:bg-white even:bg-gray-50">
              <td className="px-4 py-2 text-sm">{r.name}</td>
              <td className="px-4 py-2 text-sm">{r.role}</td>
              <td className="px-4 py-2 text-sm">{new Date(r.datetime).toLocaleString()}</td>
              <td className={`px-4 py-2 text-sm font-semibold ${r.result === 'Permitido' ? 'text-green-600' : r.result === 'Denegado' ? 'text-red-600' : 'text-yellow-600'}`}>
                {r.result}
              </td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr><td colSpan="4" className="px-4 py-6 text-center text-gray-500">Sin registros</td></tr>
          )}
        </tbody>
      </table>
    </div>
  )
}