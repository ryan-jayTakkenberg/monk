import { useState, useEffect } from 'react'
import api from '../api/client'
import BottomNav from '../components/BottomNav'
import styles from './Screen.module.css'
import s from './Home.module.css'
import type { JournalEntry } from '../types'

const QUESTIONS = [
  'What is the one thing you want to accomplish today?',
  'How is your energy and mindset right now?',
  'What would make today a win — no matter what else happens?',
  'What are you grateful for this morning?',
]

export default function Home() {
  const today = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' })
  const [entry, setEntry] = useState<JournalEntry | null>(null)
  const [completed, setCompleted] = useState(false)
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState(['', '', '', ''])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.get('/api/journal/').then((res) => {
      if (res.data.completed) {
        setEntry(res.data.entry)
        setCompleted(true)
      }
    }).finally(() => setLoading(false))
  }, [])

  async function handleNext() {
    if (step < 3) {
      setStep(step + 1)
    } else {
      setSaving(true)
      try {
        await api.post('/api/journal/', {
          answer_1: answers[0],
          answer_2: answers[1],
          answer_3: answers[2],
          answer_4: answers[3],
        })
        setCompleted(true)
      } finally {
        setSaving(false)
      }
    }
  }

  if (loading) return <div className={styles.screen}><BottomNav /></div>

  return (
    <div className={styles.screen}>
      <div className={styles.scroll}>
        <div className={styles.topRow}>
          <div>
            <h1 className={styles.greet}>Good morning</h1>
            <p className={styles.date}>{today}</p>
          </div>
        </div>

        {!completed ? (
          <div className={s.card}>
            <p className={s.stepLabel}>Question {step + 1} of 4</p>
            <p className={s.question}>{QUESTIONS[step]}</p>
            <textarea
              className={s.textarea}
              value={answers[step]}
              onChange={(e) => {
                const next = [...answers]
                next[step] = e.target.value
                setAnswers(next)
              }}
              placeholder="Type your answer..."
              rows={4}
            />
            <button
              className={s.btn}
              onClick={handleNext}
              disabled={!answers[step].trim() || saving}
            >
              {step < 3 ? 'Next' : saving ? '...' : 'Complete check-in'}
            </button>
          </div>
        ) : (
          <div className={s.card}>
            <p className={s.doneLabel}>Morning check-in done.</p>
            <p className={s.doneSub}>Don't waste this window.</p>
            {entry && (
              <div className={s.recap}>
                <p className={s.recapItem}><span>Focus</span>{entry.answer_1}</p>
                <p className={s.recapItem}><span>Energy</span>{entry.answer_2}</p>
                <p className={s.recapItem}><span>Win</span>{entry.answer_3}</p>
                <p className={s.recapItem}><span>Grateful</span>{entry.answer_4}</p>
              </div>
            )}
          </div>
        )}
      </div>
      <BottomNav />
    </div>
  )
}
