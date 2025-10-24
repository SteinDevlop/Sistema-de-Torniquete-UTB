import React, { useState } from 'react'

export default function SettingsPage() {
  const [manual, setManual] = useState(() => JSON.parse(localStorage.getItem('st_manual_gate')) || false)
  const [start, setStart] = useState(() => localStorage.getItem('st_start_time') || '07:00')
  const [end, setEnd] = useState(() => localStorage.getItem('st_end_time') || '19:00')

  function save() {
    localStorage.setItem('st_manual_gate', JSON.stringify(manual))
    localStorage.setItem('st_start_time', start)
    localStorage.setItem('st_end_time', end)
    alert('Configuraciones guardadas (local demo).')
  }

  return (
    <div className="bg-white p-4 border rounded max-w-2xl">
      <h2 className="text-xl font-semibold mb-4">Configuraciones</h2>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">Activar/desactivar torniquete manualmente</div>
            <div className="text-sm text-gray-500">Control manual simulado para la demo</div>
          </div>
          <label className="inline-flex items-center">
            <input type="checkbox" checked={manual} onChange={e => setManual(e.target.checked)} className="mr-2" />
            <span>{manual ? 'Activado' : 'Desactivado'}</span>
          </label>
        </div>

        <div>
          <div className="font-medium">Horarios permitidos</div>
          <div className="flex gap-2 mt-2">
            <input type="time" value={start} onChange={e => setStart(e.target.value)} className="border rounded px-2 py-1" />
            <span className="self-center">a</span>
            <input type="time" value={end} onChange={e => setEnd(e.target.value)} className="border rounded px-2 py-1" />
          </div>
        </div>

        <div>
          <div className="font-medium">Actualizar credenciales del sistema</div>
          <div className="text-sm text-gray-500">Funcionalidad simulada</div>
          <div className="mt-2">
            <input placeholder="Usuario sistema" className="border rounded px-2 py-1 w-full mb-2" />
            <input placeholder="Contraseña" type="password" className="border rounded px-2 py-1 w-full" />
          </div>
        </div>

        <div className="flex justify-end">
          <button onClick={save} className="px-3 py-1 bg-utb text-white rounded">Guardar cambios</button>
        </div>
      </div>
    </div>
  )
}