import React from 'react'
import logo from '../assets/logoutb.png'

export default function Header({ title, userName, onLogout }) {
  return (
    <header className="flex items-center justify-between bg-white border-b px-4 py-3">
      <div className="flex items-center gap-3">
        <img src={logo} alt="UTB" className="h-10 w-10 object-contain" />
        <div>
          <h1 className="text-lg font-semibold text-utb">{title}</h1>
          <p className="text-sm text-gray-500">Sistema de Torniquete UTB</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-sm text-gray-700">Operador: <span className="font-medium">{userName}</span></div>
        <button onClick={onLogout} className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">Cerrar sesión</button>
      </div>
    </header>
  )
}