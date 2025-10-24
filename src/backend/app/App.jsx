import React, { useEffect, useState } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import Login from './pages/Login'
import OperatorView from './pages/OperatorView'
import AdminDashboard from './pages/AdminDashboard'
import './index.css'

function App() {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('st_user')) || null
    } catch {
      return null
    }
  })

  useEffect(() => {
    localStorage.setItem('st_user', JSON.stringify(user))
  }, [user])

  return (
    <Routes>
      <Route path="/" element={<Navigate to={user ? (user.role === 'Admin' ? '/admin' : '/operator') : '/login'} replace />} />
      <Route path="/login" element={<Login onLogin={setUser} />} />
      <Route path="/operator" element={user && user.role === 'Operator' ? <OperatorView user={user} onLogout={() => setUser(null)} /> : <Navigate to="/login" />} />
      <Route path="/admin/*" element={user && user.role === 'Admin' ? <AdminDashboard user={user} onLogout={() => setUser(null)} /> : <Navigate to="/login" />} />
      <Route path="*" element={<div className="p-8">Página no encontrada</div>} />
    </Routes>
  )
}

export default App