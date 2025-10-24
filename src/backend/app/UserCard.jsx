import React from 'react'

export default function UserCard({ user }) {
  if (!user) {
    return (
      <div className="border rounded p-4 text-center text-gray-500">Ningún usuario verificado</div>
    )
  }

  return (
    <div className="border rounded p-4 bg-white shadow-sm">
      <h3 className="text-lg font-semibold">{user.name}</h3>
      <p className="text-sm text-gray-600">ID: {user.id}</p>
      <p className="text-sm">Tipo: <span className="font-medium">{user.role}</span></p>
      <p className="text-sm">Estado del carnet: <span className={user.status === 'Activo' ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>{user.status}</span></p>
      <p className="text-sm text-gray-500">Último acceso: {new Date(user.last_access).toLocaleString()}</p>
    </div>
  )
}