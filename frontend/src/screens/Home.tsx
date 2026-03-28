import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import BottomNav from '../components/BottomNav'
import styles from './Screen.module.css'
import s from './Home.module.css'
import type { JournalEntry, Suggestion } from '../types'

const QUOTES = [
  "You have power over your mind, not outside events. — Marcus Aurelius",
  "Waste no more time arguing what a good man should be. Be one. — Marcus Aurelius",
  "It is not death that a man should fear, but he should fear never beginning to live. — Marcus Aurelius",
  "The impediment to action advances action. What stands in the way becomes the way. — Marcus Aurelius",
  "Do not indulge in dreams of what you do not have, but count the blessings you actually possess. — Marcus Aurelius",
  "Luck is what happens when preparation meets opportunity. — Seneca",
  "It is not that I'm so smart. But I stay with the questions much longer. — Einstein",
  "He who conquers himself is the mightiest warrior. — Confucius",
  "Be like water making its way through cracks. — Bruce Lee",
  "The successful warrior is the average man with laser-like focus. — Bruce Lee",
  "If you always put limits on everything you do, it will spread into your work and life. — Bruce Lee",
  "The worst thing I can be is the same as everybody else. — Arnold Schwarzenegger",
  "Strength does not come from winning. Your struggles develop your strengths. — Arnold Schwarzenegger",
  "The mind is the limit. As long as the mind can envision it, you can achieve it. — Arnold Schwarzenegger",
  "Discipline is the bridge between goals and accomplishment. — Jim Rohn",
  "Take care of your body. It's the only place you have to live. — Jim Rohn",
  "Don't wish it were easier. Wish you were better. — Jim Rohn",
  "The Iron never lies to you. — Henry Rollins",
  "I believe that the way to live in peace with the Iron is to love it. — Henry Rollins",
  "No man has the right to be an amateur in the matter of physical training. — Socrates",
  "We suffer more in imagination than in reality. — Seneca",
  "Make the most of yourself, for that is all there is of you. — Ralph Waldo Emerson",
  "What you do every day matters more than what you do once in a while. — Gretchen Rubin",
  "Strong people are harder to kill than weak people. — Mark Rippetoe",
  "The goal is not to be better than the other man, but your previous self. — The Dalai Lama",
  "Pain is temporary. It may last a minute, a day, a year. But eventually it will subside. — Lance Armstrong",
  "Champions aren't made in gyms. Champions are made from something deep inside them. — Muhammad Ali",
  "Float like a butterfly, sting like a bee. — Muhammad Ali",
  "I fear not the man who has practiced 10,000 kicks, but I fear the man who has practiced one kick 10,000 times. — Bruce Lee",
  "Fall seven times, stand up eight. — Japanese Proverb",
]

const QUESTIONS = [
  'What is the one thing you want to accomplish today?',
  'How is your energy and mindset right now?',
  'What would make today a win — no matter what else happens?',
  'What are you grateful for this morning?',
]

export default function Home() {
  const navigate = useNavigate()
  const today = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' })
  const quote = QUOTES[(new Date().getDate() - 1) % QUOTES.length]
  const [entry, setEntry] = useState<JournalEntry | null>(null)
  const [completed, setCompleted] = useState(false)
  const [step, setStep] = useState(() => {
    const saved = localStorage.getItem('journal_step')
    return saved ? parseInt(saved, 10) : 0
  })
  const [answers, setAnswers] = useState<string[]>(() => {
    const saved = localStorage.getItem('journal_answers')
    return saved ? JSON.parse(saved) : ['', '', '', '']
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [recap, setRecap] = useState<string | null>(null)
  const [recapLoading, setRecapLoading] = useState(false)

  useEffect(() => {
    api.get('/api/journal/').then((res) => {
      if (res.data.completed) {
        setEntry(res.data.entry)
        setCompleted(true)
      }
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!completed) return
    api.get('/api/health/suggestions/').then((res) => {
      if (Array.isArray(res.data)) setSuggestions(res.data)
    }).catch(() => {})
    api.get('/api/journal/recap/').then((res) => {
      if (res.data.recap) setRecap(res.data.recap)
    }).catch(() => {})
  }, [completed])

  async function handleNext() {
    if (step < 3) {
      const next = step + 1
      setStep(next)
      localStorage.setItem('journal_step', String(next))
    } else {
      setSaving(true)
      try {
        await api.post('/api/journal/', {
          answer_1: answers[0],
          answer_2: answers[1],
          answer_3: answers[2],
          answer_4: answers[3],
        })
        localStorage.removeItem('journal_answers')
        localStorage.removeItem('journal_step')
        setCompleted(true)
      } finally {
        setSaving(false)
      }
    }
  }

  async function generateRecap() {
    setRecapLoading(true)
    try {
      const res = await api.post('/api/journal/recap/')
      setRecap(res.data.recap)
    } catch {
      // no entries or Claude failed — silently ignore
    } finally {
      setRecapLoading(false)
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
          <button className={s.settingsBtn} onClick={() => navigate('/settings')} aria-label="Settings">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <circle cx="9" cy="9" r="2.5" stroke="var(--txt2)" strokeWidth="1.25"/>
              <path d="M9 1v2M9 15v2M1 9h2M15 9h2M3.22 3.22l1.42 1.42M13.36 13.36l1.42 1.42M3.22 14.78l1.42-1.42M13.36 4.64l1.42-1.42" stroke="var(--txt2)" strokeWidth="1.25" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        {/* Daily quote */}
        <div className={s.quoteCard}>
          <p className={s.quoteText}>{quote}</p>
        </div>

        {/* Journal check-in */}
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
                localStorage.setItem('journal_answers', JSON.stringify(next))
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

        {/* AI Suggestions */}
        {completed && suggestions.length > 0 && (
          <div className={s.section}>
            <p className={s.sectionLabel}>What to do today</p>
            {suggestions.map((s_item, i) => (
              <div key={i} className={s.suggestionCard}>
                <p className={s.suggestionTitle}>{s_item.title}</p>
                <p className={s.suggestionDesc}>{s_item.description}</p>
              </div>
            ))}
          </div>
        )}

        {/* Weekly recap */}
        {completed && (
          <div className={s.section}>
            <p className={s.sectionLabel}>Weekly recap</p>
            {recap ? (
              <div className={s.recapCard}>
                <p className={s.recapText}>{recap}</p>
              </div>
            ) : (
              <button
                className={s.recapBtn}
                onClick={generateRecap}
                disabled={recapLoading}
              >
                {recapLoading ? 'Generating...' : 'Generate this week\'s recap'}
              </button>
            )}
          </div>
        )}
      </div>
      <BottomNav />
    </div>
  )
}
