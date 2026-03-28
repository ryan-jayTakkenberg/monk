import { useNavigate } from 'react-router-dom'
import BottomNav from '../components/BottomNav'
import styles from './Screen.module.css'
import s from './Settings.module.css'

export default function Settings() {
  const navigate = useNavigate()
  const username = localStorage.getItem('username') ?? 'User'

  function logout() {
    localStorage.clear()
    navigate('/login', { replace: true })
  }

  return (
    <div className={styles.screen}>
      <div className={styles.scroll}>
        <h1 className={styles.pageTitle}>Settings</h1>

        <div className={s.card}>
          <p className={s.label}>Account</p>
          <p className={s.value}>{username}</p>
        </div>

        <button className={s.logoutBtn} onClick={logout}>
          Sign out
        </button>
      </div>
      <BottomNav />
    </div>
  )
}
