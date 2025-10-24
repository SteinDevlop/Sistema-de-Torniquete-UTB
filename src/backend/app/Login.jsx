import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login({ onLogin }) {
  const navigate = useNavigate()

  function handleLogin(role) {
    const mock = role === 'Admin'
      ? { username: 'admin.utb', role: 'Admin', name: 'Administrador' }
      : { username: 'operator.utb', role: 'Operator', name: 'Operador' }

    onLogin(mock)
    navigate(role === 'Admin' ? '/admin' : '/operator')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-utb to-white p-6">
      <div className="bg-white rounded shadow-lg max-w-md w-full p-6">
        <h2 className="text-2xl font-bold text-utb mb-4">Sistema de Torniquete UTB</h2>
        <p className="mb-4 text-gray-600">Seleccione el tipo de sesión para la demo</p>
        <div className="flex gap-3">
          <button onClick={() => handleLogin('Operator')} className="flex-1 bg-utb text-white px-4 py-2 rounded hover:brightness-95">Entrar como Operador</button>
          <button onClick={() => handleLogin('Admin')} className="flex-1 bg-gray-800 text-white px-4 py-2 rounded hover:brightness-95">Entrar como Administrador</button>
        </div>
        <div className="mt-6 text-xs text-gray-500">
          Datos simulados extraídos del repositorio Steindevlop (uso local y demo).
        </div>
      </div>
    </div>
  )
}
