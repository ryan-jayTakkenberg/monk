import { useState, useEffect } from 'react'
import api from '../api/client'
import BottomNav from '../components/BottomNav'
import styles from './Screen.module.css'
import s from './Sleep.module.css'
import type { SleepData } from '../types'

function recoveryColor(score: number) {
  if (score >= 67) return '#27ae60'
  if (score >= 34) return '#e67e22'
  return '#c0392b'
}

export default function Sleep() {
  const [data, setData] = useState<SleepData | null>(null)
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/whoop/status/').then((res) => {
      setConnected(res.data.connected)
      setData(res.data.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className={styles.screen}><BottomNav /></div>

  return (
    <div className={styles.screen}>
      <div className={styles.scroll}>
        <h1 className={styles.pageTitle}>Sleep & Recovery</h1>

        {!connected ? (
          <div className={s.card}>
            <p className={s.notConnected}>Whoop not connected.</p>
            <p className={s.notConnectedSub}>Connect your Whoop device to see sleep and recovery data.</p>
          </div>
        ) : !data ? (
          <div className={s.card}>
            <p className={s.notConnected}>No data yet.</p>
            <p className={s.notConnectedSub}>Whoop is connected. Sync to load the latest data.</p>
          </div>
        ) : (
          <>
            {/* Recovery */}
            <div className={s.card}>
              <p className={s.cardLabel}>Recovery</p>
              <p className={s.recoveryScore} style={{ color: recoveryColor(data.recovery_score) }}>
                {data.recovery_score}%
              </p>
            </div>

            {/* Sleep */}
            <div className={s.card}>
              <p className={s.cardLabel}>Sleep</p>
              <p className={s.bigStat}>{data.duration_hours.toFixed(1)}<span>h</span></p>
              <div className={s.stageBars}>
                <div className={s.stageBar} style={{ flex: data.awake_pct }}>
                  <div className={s.stageBarFill} style={{ background: '#ccc' }} />
                  <p className={s.stageLabel}>Awake {data.awake_pct}%</p>
                </div>
                <div className={s.stageBar} style={{ flex: data.light_pct }}>
                  <div className={s.stageBarFill} style={{ background: 'var(--acc-mid)' }} />
                  <p className={s.stageLabel}>Light {data.light_pct}%</p>
                </div>
                <div className={s.stageBar} style={{ flex: data.deep_pct }}>
                  <div className={s.stageBarFill} style={{ background: 'var(--acc-dark)' }} />
                  <p className={s.stageLabel}>Deep {data.deep_pct}%</p>
                </div>
              </div>
            </div>

            {/* HRV */}
            <div className={s.card}>
              <p className={s.cardLabel}>HRV</p>
              <p className={s.bigStat}>{Math.round(data.hrv)}<span>ms</span></p>
            </div>
          </>
        )}
      </div>
      <BottomNav />
    </div>
  )
}
