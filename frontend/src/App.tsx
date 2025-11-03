import { Routes, Route, NavLink } from 'react-router-dom'
import WorkersPage from './pages/WorkersPage'
import CalendarPage from './pages/CalendarPage'
import SchedulePage from './pages/SchedulePage'
import './styles.css'

export default function App() {
  return (
    <div>
      <nav aria-label="Main">
        <ul className="nav">
          <li><NavLink to="/" className={({isActive}) => isActive ? 'active' : ''} end>Workers</NavLink></li>
          <li><NavLink to="/calendar" className={({isActive}) => isActive ? 'active' : ''}>Calendar</NavLink></li>
          <li><NavLink to="/schedule" className={({isActive}) => isActive ? 'active' : ''}>Today's Schedule</NavLink></li>
        </ul>
      </nav>
      <main className="container">
        <Routes>
          <Route path="/" element={<WorkersPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/schedule" element={<SchedulePage />} />
        </Routes>
      </main>
    </div>
  )
}

