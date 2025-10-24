import React, { useEffect, useState } from 'react'
import usersJson from '../data/users.json'

export default function UsersPage() {
  const [users, setUsers] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('st_users')) || usersJson
    } catch {
      return usersJson
    }
  })
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ id: '', name: '', role: 'Estudiante', status: 'Activo' })
  const [editingIndex, setEditingIndex] = useState(null)

  useEffect(() => {
    localStorage.setItem('st_users', JSON.stringify(users))
  }, [users])

  function openAdd() {
    setForm({ id: '', name: '', role: 'Estudiante', status: 'Activo' })
    setEditingIndex(null)
    setShowForm(true)
  }

  function openEdit(i) {
    setForm(users[i])
    setEditingIndex(i)
    setShowForm(true)
  }

  function save() {
    if (!form.id || !form.name) return alert('ID y Nombre son obligatorios')
    if (editingIndex === null) {
      setUsers(prev => [form, ...prev])
    } else {
      setUsers(prev => prev.map((u, i) => i === editingIndex ? form : u))
    }
    setShowForm(false)
  }

  function remove(i) {
    if (!confirm('Eliminar usuario?')) return
    setUsers(prev => prev.filter((_, idx) => idx !== i))
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Usuarios</h2>
        <div>
          <button onClick={openAdd} className="bg-utb text-white px-3 py-1 rounded">Agregar</button>
        </div>
      </div>

      <div className="bg-white border rounded overflow-auto">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-sm">ID</th>
              <th className="px-4 py-2 text-sm">Nombre</th>
              <th className="px-4 py-2 text-sm">Rol</th>
              <th className="px-4 py-2 text-sm">Estado</th>
              <th className="px-4 py-2 text-sm">Último acceso</th>
              <th className="px-4 py-2 text-sm">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u, i) => (
              <tr key={u.id} className="odd:bg-white even:bg-gray-50">
                <td className="px-4 py-2">{u.id}</td>
                <td className="px-4 py-2">{u.name}</td>
                <td className="px-4 py-2">{u.role}</td>
                <td className="px-4 py-2">{u.status}</td>
                <td className="px-4 py-2">{u.last_access ? new Date(u.last_access).toLocaleString() : '-'}</td>
                <td className="px-4 py-2">
                  <button onClick={() => openEdit(i)} className="text-sm text-blue-600 mr-2">Editar</button>
                  <button onClick={() => remove(i)} className="text-sm text-red-600">Eliminar</button>
                </td>
              </tr>
            ))}
            {users.length === 0 && <tr><td colSpan="6" className="p-4 text-center text-gray-500">Sin usuarios</td></tr>}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-3">{editingIndex === null ? 'Agregar usuario' : 'Editar usuario'}</h3>
            <div className="space-y-2">
              <div>
                <label className="block text-sm">ID / Código</label>
                <input value={form.id} onChange={e => setForm({ ...form, id: e.target.value })} className="w-full border rounded px-2 py-1" />
              </div>
              <div>
                <label className="block text-sm">Nombre</label>
                <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full border rounded px-2 py-1" />
              </div>
              <div>
                <label className="block text-sm">Rol</label>
                <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} className="w-full border rounded px-2 py-1">
                  <option>Estudiante</option>
                  <option>Profesor</option>
                  <option>Administrativo</option>
                </select>
              </div>
              <div>
                <label className="block text-sm">Estado</label>
                <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })} className="w-full border rounded px-2 py-1">
                  <option>Activo</option>
                  <option>Inactivo</option>
                </select>
              </div>
            </div>

            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setShowForm(false)} className="px-3 py-1 rounded border">Cancelar</button>
              <button onClick={save} className="px-3 py-1 rounded bg-utb text-white">Guardar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}