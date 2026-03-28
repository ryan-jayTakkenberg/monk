import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import BottomNav from '../components/BottomNav'
import api from '../api/client'
import type { MealSettings } from '../types'
import styles from './Screen.module.css'
import s from './Settings.module.css'

export default function Settings() {
  const navigate = useNavigate()
  const username = localStorage.getItem('username') ?? 'User'
  const [isDark, setIsDark] = useState(
    () => localStorage.getItem('theme') !== 'light'
  )

  const [kcalGoal, setKcalGoal] = useState<number>(2500)
  const [proteinGoal, setProteinGoal] = useState<number>(180)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const savedTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    api.get<MealSettings>('/api/meals/settings/').then((res) => {
      setKcalGoal(res.data.kcal_goal)
      setProteinGoal(res.data.protein_goal_g)
    })
  }, [])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? '' : 'light')
    localStorage.setItem('theme', isDark ? 'dark' : 'light')
  }, [isDark])

  async function saveGoals() {
    setSaving(true)
    try {
      await api.patch<MealSettings>('/api/meals/settings/', {
        kcal_goal: kcalGoal,
        protein_goal_g: proteinGoal,
      })
      setSaved(true)
      if (savedTimer.current) clearTimeout(savedTimer.current)
      savedTimer.current = setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

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

        <div className={s.card}>
          <p className={s.label}>Daily goals</p>
          <div className={s.goalRow}>
            <label className={s.goalLabel} htmlFor="kcal-goal">
              Daily kcal goal
            </label>
            <input
              id="kcal-goal"
              className={s.goalInput}
              type="number"
              min={500}
              max={10000}
              value={kcalGoal}
              onChange={(e) => setKcalGoal(Number(e.target.value))}
            />
          </div>
          <div className={s.goalRow}>
            <label className={s.goalLabel} htmlFor="protein-goal">
              Protein goal (g)
            </label>
            <input
              id="protein-goal"
              className={s.goalInput}
              type="number"
              min={10}
              max={500}
              value={proteinGoal}
              onChange={(e) => setProteinGoal(Number(e.target.value))}
            />
          </div>
          <div className={s.saveRow}>
            <button className={s.saveBtn} onClick={saveGoals} disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </button>
            {saved && <span className={s.savedConfirm}>Saved</span>}
          </div>
        </div>

        <div className={s.card}>
          <div className={s.row}>
            <div>
              <p className={s.label}>Appearance</p>
              <p className={s.value}>{isDark ? 'Dark' : 'Light'}</p>
            </div>
            <button className={s.toggle} onClick={() => setIsDark(!isDark)} aria-label="Toggle theme">
              {isDark ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="var(--txt2)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="5" stroke="var(--txt2)" strokeWidth="1.5"/>
                  <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="var(--txt2)" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        <button className={s.logoutBtn} onClick={logout}>
          Sign out
        </button>
      </div>
      <BottomNav />
    </div>
  )
}
