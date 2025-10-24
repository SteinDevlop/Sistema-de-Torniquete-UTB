import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import UsersPage from './UsersPage'
import AccessPage from './AccessPage'
import ReportsPage from './ReportsPage'
import SettingsPage from './SettingsPage'

export default function AdminDashboard({ user, onLogout }) {
  return (
    <div className="min-h-screen flex bg-gray-50">
      <Sidebar onLogout={onLogout} />
      <div className="flex-1 flex flex-col">
        <Header title="Sistema de Torniquete UTB – Panel Administrador" userName={user.name} onLogout={onLogout} />
        <main className="p-6">
          <Routes>
            <Route path="/" element={<Navigate to="users" replace />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="accesses" element={<AccessPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}