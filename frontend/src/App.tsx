import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Home from './screens/Home'
import Food from './screens/Food'
import Sleep from './screens/Sleep'
import Login from './screens/Login'
import Settings from './screens/Settings'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token')
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
        <Route path="/food" element={<PrivateRoute><Food /></PrivateRoute>} />
        <Route path="/sleep" element={<PrivateRoute><Sleep /></PrivateRoute>} />
        <Route path="/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
