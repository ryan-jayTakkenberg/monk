import { useState, useEffect, useRef } from 'react'
import api from '../api/client'
import BottomNav from '../components/BottomNav'
import styles from './Screen.module.css'
import s from './Food.module.css'
import type { Meal, MealTotals, MealAnalysis } from '../types'

const KCAL_GOAL = 2000
const R = 58
const CIRC = 2 * Math.PI * R

type UploadStep = 'idle' | 'analyzing' | 'confirm' | 'saving'

export default function Food() {
  const [meals, setMeals] = useState<Meal[]>([])
  const [totals, setTotals] = useState<MealTotals>({ kcal: 0, protein_g: 0, carbs_g: 0, fat_g: 0 })
  const [loading, setLoading] = useState(true)
  const [step, setStep] = useState<UploadStep>('idle')
  const [preview, setPreview] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<MealAnalysis | null>(null)
  const [photoFile, setPhotoFile] = useState<File | null>(null)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  function fetchMeals() {
    return api.get('/api/meals/').then((res) => {
      setMeals(res.data.meals)
      setTotals(res.data.totals)
    })
  }

  useEffect(() => {
    fetchMeals().finally(() => setLoading(false))
  }, [])

  function handleFile(file: File) {
    setPhotoFile(file)
    setPreview(URL.createObjectURL(file))
    setStep('analyzing')
    setError('')

    const form = new FormData()
    form.append('photo', file)
    api.post('/api/meals/analyze/', form).then((res) => {
      setAnalysis(res.data)
      setStep('confirm')
    }).catch(() => {
      setError('Could not analyze photo. Try again.')
      setStep('idle')
      setPreview(null)
    })
  }

  async function confirmMeal() {
    if (!analysis || !photoFile) return
    setStep('saving')
    const form = new FormData()
    form.append('name', analysis.name)
    form.append('kcal', String(analysis.kcal))
    form.append('protein_g', String(analysis.protein_g))
    form.append('carbs_g', String(analysis.carbs_g))
    form.append('fat_g', String(analysis.fat_g))
    form.append('photo', photoFile)
    await api.post('/api/meals/', form)
    await fetchMeals()
    setStep('idle')
    setPreview(null)
    setAnalysis(null)
    setPhotoFile(null)
  }

  async function deleteMeal(id: number) {
    setDeletingId(id)
    try {
      await api.delete(`/api/meals/${id}/`)
      setMeals((prev) => prev.filter((m) => m.id !== id))
      setTotals((prev) => {
        const removed = meals.find((m) => m.id === id)
        if (!removed) return prev
        return {
          kcal: prev.kcal - removed.kcal,
          protein_g: prev.protein_g - removed.protein_g,
          carbs_g: prev.carbs_g - removed.carbs_g,
          fat_g: prev.fat_g - removed.fat_g,
        }
      })
    } finally {
      setDeletingId(null)
    }
  }

  function cancel() {
    setStep('idle')
    setPreview(null)
    setAnalysis(null)
    setPhotoFile(null)
    setError('')
  }

  const progress = Math.min(totals.kcal / KCAL_GOAL, 1)
  const offset = CIRC * (1 - progress)

  if (loading) return <div className={styles.screen}><BottomNav /></div>

  return (
    <div className={styles.screen}>
      <div className={styles.scroll}>
        <h1 className={styles.pageTitle}>Food log</h1>

        {/* Kcal ring */}
        <div className={s.ringWrap}>
          <svg width="140" height="140" viewBox="0 0 140 140">
            <circle cx="70" cy="70" r={R} fill="none" stroke="var(--bg3)" strokeWidth="10" />
            <circle
              cx="70" cy="70" r={R}
              fill="none"
              stroke="var(--acc)"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={CIRC}
              strokeDashoffset={offset}
              transform="rotate(-90 70 70)"
            />
          </svg>
          <div className={s.ringInner}>
            <p className={s.ringKcal}>{totals.kcal}</p>
            <p className={s.ringLabel}>/ {KCAL_GOAL} kcal</p>
          </div>
        </div>

        {/* Macros */}
        <div className={s.macroRow}>
          <div className={s.macro}>
            <p className={s.macroVal}>{Math.round(totals.protein_g)}g</p>
            <p className={s.macroName}>Protein</p>
          </div>
          <div className={s.macro}>
            <p className={s.macroVal}>{Math.round(totals.carbs_g)}g</p>
            <p className={s.macroName}>Carbs</p>
          </div>
          <div className={s.macro}>
            <p className={s.macroVal}>{Math.round(totals.fat_g)}g</p>
            <p className={s.macroName}>Fat</p>
          </div>
        </div>

        {/* Upload flow */}
        {step === 'idle' && (
          <>
            {error && <p className={s.error}>{error}</p>}
            <button className={s.logBtn} onClick={() => inputRef.current?.click()}>
              Log meal with photo
            </button>
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              capture="environment"
              style={{ display: 'none' }}
              onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]) }}
            />
          </>
        )}

        {step === 'analyzing' && (
          <div className={s.sheet}>
            {preview && <img src={preview} className={s.photoPreview} alt="meal" />}
            <p className={s.sheetStatus}>Analyzing...</p>
          </div>
        )}

        {step === 'confirm' && analysis && (
          <div className={s.sheet}>
            {preview && <img src={preview} className={s.photoPreview} alt="meal" />}
            <p className={s.mealName}>{analysis.name}</p>
            <div className={s.analysisRow}>
              <span>{analysis.kcal} kcal</span>
              <span>{analysis.protein_g}g P</span>
              <span>{analysis.carbs_g}g C</span>
              <span>{analysis.fat_g}g F</span>
            </div>
            <div className={s.sheetActions}>
              <button className={s.cancelBtn} onClick={cancel}>Cancel</button>
              <button className={s.confirmBtn} onClick={confirmMeal}>Save meal</button>
            </div>
          </div>
        )}

        {step === 'saving' && (
          <div className={s.sheet}>
            <p className={s.sheetStatus}>Saving...</p>
          </div>
        )}

        {/* Meal list */}
        {meals.length > 0 && (
          <div className={s.mealList}>
            {meals.map((m) => (
              <div key={m.id} className={s.mealRow}>
                {m.photo && <img src={m.photo} className={s.thumb} alt={m.name} />}
                <div className={s.mealInfo}>
                  <p className={s.mealRowName}>{m.name}</p>
                  <p className={s.mealRowMacros}>{m.kcal} kcal · {m.protein_g}g P · {m.carbs_g}g C · {m.fat_g}g F</p>
                </div>
                <button
                  className={`${s.deleteBtn}${deletingId === m.id ? ` ${s.deleteBtnBusy}` : ''}`}
                  onClick={() => deleteMeal(m.id)}
                  disabled={deletingId !== null}
                  aria-label={`Delete ${m.name}`}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <polyline points="3 6 5 6 21 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M19 6l-1 14H6L5 6M10 11v6M14 11v6M9 6V4h6v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
      <BottomNav />
    </div>
  )
}
