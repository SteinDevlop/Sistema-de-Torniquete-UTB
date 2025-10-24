import React from 'react'
import logo from '../assets/logoutb.png'
import { NavLink } from 'react-router-dom'

export default function Sidebar({ onLogout }) {
  const links = [
    { to: 'users', label: 'Usuarios' },
    { to: 'accesses', label: 'Accesos' },
    { to: 'reports', label: 'Reportes' },
    { to: 'settings', label: 'Configuraciones' }
  ]

  return (
    <aside className="bg-white border-r w-64 p-4 hidden md:block">
      <div className="flex items-center gap-3 mb-6">
        <img src={logo} alt="UTB" className="h-10 w-10" />
        <div>
          <div className="font-bold text-utb">UTB</div>
          <div className="text-xs text-gray-500">Sistema Torniquete</div>
        </div>
      </div>
      <nav className="flex flex-col gap-2">
        {links.map(l => (
          <NavLink key={l.to} to={l.to} className={({ isActive }) => `px-3 py-2 rounded ${isActive ? 'bg-utb text-white' : 'text-gray-700 hover:bg-gray-100'}`}>
            {l.label}
          </NavLink>
        ))}
        <button onClick={onLogout} className="mt-4 px-3 py-2 rounded bg-red-500 text-white hover:bg-red-600">Cerrar sesión</button>
      </nav>
    </aside>
  )
}