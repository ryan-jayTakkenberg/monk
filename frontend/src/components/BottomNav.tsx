import { useNavigate, useLocation } from 'react-router-dom'
import styles from './BottomNav.module.css'

const tabs = [
  {
    path: '/',
    label: 'Home',
    icon: (active: boolean) => (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
        <path d="M2 9L9 3l7 6" stroke={active ? 'var(--acc)' : 'var(--txt2)'} strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M4 8v7h10V8" stroke={active ? 'var(--acc)' : 'var(--txt2)'} strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    path: '/food',
    label: 'Food',
    icon: (active: boolean) => (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
        <rect x="3" y="7" width="12" height="8" rx="2" stroke={active ? 'var(--acc)' : 'var(--txt2)'} strokeWidth="1.25"/>
        <path d="M6 7V5.5a3 3 0 016 0V7" stroke={active ? 'var(--acc)' : 'var(--txt2)'} strokeWidth="1.25"/>
      </svg>
    ),
  },
  {
    path: '/sleep',
    label: 'Sleep',
    icon: (active: boolean) => (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
        <path d="M14 10A6 6 0 018 4a6 6 0 00-1 11.9A6 6 0 0014 10z" stroke={active ? 'var(--acc)' : 'var(--txt2)'} strokeWidth="1.25"/>
      </svg>
    ),
  },
]

export default function BottomNav() {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  return (
    <nav className={styles.nav}>
      {tabs.map((tab) => {
        const active = pathname === tab.path
        return (
          <button
            key={tab.path}
            className={`${styles.btn} ${active ? styles.active : ''}`}
            onClick={() => navigate(tab.path)}
          >
            {tab.icon(active)}
            <span className={styles.label}>{tab.label}</span>
          </button>
        )
      })}
    </nav>
  )
}
