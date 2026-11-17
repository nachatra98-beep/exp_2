import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Home } from './pages/Home';
import { AddHabit } from './pages/AddHabit';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Main Habit Tracker Dashboard as default landing page */}
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />

          {/* Add / Edit Habit Route */}
          <Route path="/add" element={<AddHabit />} />

          {/* Catch-all redirect directly to Dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
