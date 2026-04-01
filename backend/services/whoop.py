import requests

WHOOP_BASE = 'https://api.prod.whoop.com/developer/v1'


def get_today_data(access_token: str) -> dict:
    """Fetch latest recovery + sleep from Whoop API. Returns dict ready to save into WhoopSleepRecord."""
    headers = {'Authorization': f'Bearer {access_token}'}

    recovery_resp = requests.get(f'{WHOOP_BASE}/recovery', headers=headers, timeout=10)
    sleep_resp    = requests.get(f'{WHOOP_BASE}/activity/sleep', headers=headers, timeout=10)

    if recovery_resp.status_code == 401 or sleep_resp.status_code == 401:
        raise PermissionError('Whoop token expired.')

    recovery_resp.raise_for_status()
    sleep_resp.raise_for_status()

    recovery_data = recovery_resp.json()
    sleep_data    = sleep_resp.json()

    latest_recovery = (recovery_data.get('records') or [{}])[0]
    latest_sleep    = (sleep_data.get('records') or [{}])[0]

    rec_score = latest_recovery.get('score', {})
    slp_score = latest_sleep.get('score', {})

    total_ms   = slp_score.get('total_in_bed_time_milli', 0) or 0
    duration_h = round(total_ms / 3_600_000, 2) if total_ms else None
    awake_pct  = slp_score.get('awake_pct', None)
    light_pct  = slp_score.get('light_pct', None)
    deep_pct   = slp_score.get('slow_wave_sleep_pct', None)

    return {
        'recovery_score': rec_score.get('recovery_score'),
        'hrv':            rec_score.get('hrv_rmssd_milli'),
        'duration_hours': duration_h,
        'awake_pct':      awake_pct,
        'light_pct':      light_pct,
        'deep_pct':       deep_pct,
    }
