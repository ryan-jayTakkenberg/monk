import { useState, useEffect } from 'react'
import api from '../api/client'
import BottomNav from '../components/BottomNav'
import styles from './Screen.module.css'
import s from './Sleep.module.css'
import type { SleepData, HistoryEntry, Suggestion } from '../types'

function recoveryColor(score: number) {
  if (score >= 67) return '#27ae60'
  if (score >= 34) return '#e67e22'
  return '#c0392b'
}

export default function Sleep() {
  const [data, setData] = useState<SleepData | null>(null)
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [syncError, setSyncError] = useState('')
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [insights, setInsights] = useState<Suggestion[]>([])
  const [insightsLoading, setInsightsLoading] = useState(false)

  function fetchInsights() {
    setInsightsLoading(true)
    api.get<Suggestion[]>('/api/whoop/suggestions/').then((res) => {
      setInsights(res.data)
    }).catch(() => {
      // insights are non-critical — fail silently
    }).finally(() => {
      setInsightsLoading(false)
    })
  }

  function fetchStatus() {
    return api.get('/api/whoop/status/').then((res) => {
      setConnected(res.data.connected)
      setData(res.data.data)
      if (res.data.data !== null) {
        fetchInsights()
      }
    })
  }

  function fetchHistory() {
    api.get<HistoryEntry[]>('/api/whoop/history/').then((res) => {
      setHistory(res.data)
    }).catch(() => {
      // history is non-critical — fail silently
    })
  }

  useEffect(() => {
    fetchStatus().finally(() => setLoading(false))
    fetchHistory()
  }, [])

  async function sync() {
    setSyncing(true)
    setSyncError('')
    try {
      const res = await api.get('/api/whoop/sync/')
      setData(res.data)
      fetchInsights()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { error?: string } } })?.response?.data?.error
      setSyncError(msg ?? 'Sync failed.')
    } finally {
      setSyncing(false)
    }
  }

  if (loading) return (
    <div className={styles.screen}>
      <div className={styles.scroll}>
        <div className={styles.topRow}>
          <div className={styles.skeletonLineLg} style={{ width: '160px' }} />
        </div>
        <div className={styles.skeletonCard}>
          <div className={styles.skeletonLineSm} style={{ width: '70px' }} />
          <div className={styles.skeletonBlock} style={{ height: '52px', width: '80px', marginTop: '0.4rem' }} />
        </div>
        <div className={styles.skeletonCard}>
          <div className={styles.skeletonLineSm} style={{ width: '50px' }} />
          <div className={styles.skeletonBlock} style={{ height: '42px', width: '100px', marginTop: '0.4rem', marginBottom: '1rem' }} />
          <div className={styles.skeletonBlock} style={{ height: '8px', borderRadius: '4px' }} />
        </div>
        <div className={styles.skeletonCard}>
          <div className={styles.skeletonLineSm} style={{ width: '40px' }} />
          <div className={styles.skeletonBlock} style={{ height: '42px', width: '90px', marginTop: '0.4rem' }} />
        </div>
      </div>
      <BottomNav />
    </div>
  )

  return (
    <div className={styles.screen}>
      <div className={styles.scroll}>
        <div className={styles.topRow}>
          <h1 className={styles.pageTitle}>Sleep & Recovery</h1>
          {connected && (
            <button className={s.syncBtn} onClick={sync} disabled={syncing}>
              {syncing ? '...' : 'Sync'}
            </button>
          )}
        </div>

        {syncError && <p className={s.error}>{syncError}</p>}

        {!connected ? (
          <div className={s.card}>
            <p className={s.notConnected}>Whoop not connected.</p>
            <p className={s.notConnectedSub}>Connect your Whoop device to see sleep and recovery data.</p>
          </div>
        ) : !data ? (
          <div className={s.card}>
            <p className={s.notConnected}>No data yet.</p>
            <p className={s.notConnectedSub}>Press Sync to load the latest data from Whoop.</p>
          </div>
        ) : (
          <>
            <div className={s.card}>
              <p className={s.cardLabel}>Recovery</p>
              <p className={s.recoveryScore} style={{ color: recoveryColor(data.recovery_score) }}>
                {data.recovery_score}%
              </p>
            </div>

            <div className={s.card}>
              <p className={s.cardLabel}>Sleep</p>
              <p className={s.bigStat}>{data.duration_hours.toFixed(1)}<span>h</span></p>
              <div className={s.stageBars}>
                <div className={s.stageBar} style={{ flex: data.awake_pct || 1 }}>
                  <div className={s.stageBarFill} style={{ background: '#ccc' }} />
                  <p className={s.stageLabel}>Awake {data.awake_pct}%</p>
                </div>
                <div className={s.stageBar} style={{ flex: data.light_pct || 1 }}>
                  <div className={s.stageBarFill} style={{ background: 'var(--acc-mid)' }} />
                  <p className={s.stageLabel}>Light {data.light_pct}%</p>
                </div>
                <div className={s.stageBar} style={{ flex: data.deep_pct || 1 }}>
                  <div className={s.stageBarFill} style={{ background: 'var(--acc-dark)' }} />
                  <p className={s.stageLabel}>Deep {data.deep_pct}%</p>
                </div>
              </div>
            </div>

            <div className={s.card}>
              <p className={s.cardLabel}>HRV</p>
              <p className={s.bigStat}>{Math.round(data.hrv)}<span>ms</span></p>
            </div>

            {history.length > 0 && (() => {
              const MAX_HOURS = 10
              const todayStr = history[history.length - 1]?.date
              return (
                <div className={s.card}>
                  <p className={s.cardLabel}>7-day sleep</p>
                  <div className={s.barChart}>
                    {history.map((entry) => {
                      const heightPct = Math.min((entry.duration_hours / MAX_HOURS) * 100, 100)
                      const dayLabel = new Date(entry.date).toLocaleDateString('en-US', { weekday: 'short' })
                      const isToday = entry.date === todayStr
                      return (
                        <div key={entry.date} className={s.barCol}>
                          <p className={s.barValue}>{entry.duration_hours.toFixed(1)}h</p>
                          <div className={s.barTrack}>
                            <div
                              className={s.barFill}
                              style={{
                                height: `${heightPct}%`,
                                background: isToday ? 'var(--acc)' : 'var(--bg3)',
                              }}
                            />
                          </div>
                          <p className={s.barDay}>{dayLabel}</p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })()}

            <div className={s.insightsSection}>
              <div className={s.insightsHeader}>
                <p className={s.insightsSectionLabel}>Today's focus</p>
                <button
                  className={s.refreshBtn}
                  onClick={fetchInsights}
                  disabled={insightsLoading}
                >
                  {insightsLoading ? '...' : 'Refresh'}
                </button>
              </div>
              {insights.slice(0, 3).map((item, i) => (
                <div key={i} className={s.insightCard}>
                  <p className={s.insightTitle}>{item.title}</p>
                  <p className={s.insightDesc}>{item.description}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
      <BottomNav />
    </div>
  )
}
