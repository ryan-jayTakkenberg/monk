# Monk — Mind. Body. Rest.

> Built for men who don't miss days.

## What is Monk?

Monk is a men's health and discipline app that combines AI-powered food tracking, wearable data (Whoop / Apple Health), and a daily journal into one focused experience. The goal is simple: open the app in the morning, know what to do, close the app and execute.

No noise. No gamification. No streaks. Just data and discipline.

---

## Core pillars

### Mind — Daily journal
Every morning the app asks 4 questions:
1. What is the one thing you want to accomplish today?
2. How is your energy and mindset right now?
3. What would make today a win — no matter what else happens?
4. What are you grateful for this morning?

Answers are stored per day. Every Sunday, Claude generates a written weekly recap — a direct, honest summary of patterns across the week. No fluff, no softness. Coaching tone.

### Body — AI food tracking
Users take a photo of their meal. Claude Vision analyzes the image and returns estimated kcal, protein, carbs, and fat. No manual logging, no barcode scanning. Just a photo. Results are saved to the daily food log. A kcal ring shows progress toward the daily goal (default 2000 kcal).

### Rest — Sleep & recovery
Synced from Whoop (primary) or Apple HealthKit (fallback). Displays:
- Sleep duration and stage breakdown (awake / light / deep)
- Recovery score (0–100%)
- HRV (heart rate variability)
- AI-generated insight based on today's data — what it means, whether to train hard or rest, what to do tomorrow

---

## Tech stack

### Frontend
- **PWA** (Progressive Web App) — HTML, vanilla JS, CSS
- Installable on iPhone and Android from browser
- Fonts: Bebas Neue (headlines/numbers), Barlow (body/UI)
- Accent color: `#1A6FD4` (steel blue), `#0C4A9E` (navy)
- No yellow. No gradients. Clean, masculine, flat design.

### Backend
- **Django** (Python) — REST API
- **PostgreSQL** — primary database
- **Django Allauth** — user authentication + OAuth2 for Whoop
- **Anthropic Python SDK** — Claude API calls (food analysis + journal recap)
- **Pillow** — image handling for meal photos
- Deploy target: **Railway** or **Render**

### Infrastructure
- **Terraform** — infrastructure as code
- Environment variables for all API keys (never hardcoded)

### External APIs
- **Anthropic Claude API** — `claude-sonnet-4-6` for food photo analysis and weekly journal recap
- **Whoop REST API** — `api.prod.whoop.com/developer/v1/` for recovery, HRV, sleep
- **Apple HealthKit** — via `react-native-health` if native app is built later

---

## Django models

```python
class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    answer_1 = models.TextField()  # One thing to accomplish
    answer_2 = models.TextField()  # Energy and mindset
    answer_3 = models.TextField()  # What makes today a win
    answer_4 = models.TextField()  # Gratitude

class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    kcal = models.IntegerField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()
    photo = models.ImageField(upload_to='meals/')
    logged_at = models.DateTimeField(auto_now_add=True)

class WeeklyRecap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start = models.DateField()
    ai_summary = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)

class WhoopToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
```

---

## Key API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/meals/analyze/` | Upload photo → Claude returns kcal + macros |
| POST | `/api/meals/` | Save meal to database |
| GET | `/api/meals/today/` | Get today's meals and total kcal |
| POST | `/api/journal/` | Save daily journal entry |
| GET | `/api/journal/week/` | Get this week's entries |
| POST | `/api/journal/recap/` | Trigger Claude weekly recap generation |
| GET | `/api/whoop/sync/` | Pull latest recovery + sleep from Whoop |
| GET | `/api/health/today/` | Aggregated health data for home screen |

---

## Claude API usage

### Food photo analysis
```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=250,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": 'Analyze this food. Reply ONLY with JSON: {"name":"...","kcal":0,"protein_g":0,"carbs_g":0,"fat_g":0}'}
        ]
    }]
)
```

### Weekly journal recap
```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=300,
    messages=[{
        "role": "user",
        "content": f"You are a direct, no-nonsense coach writing a weekly recap for a man. Based on his journal entries below, write 3-4 sentences. Be honest, specific, mention patterns. No fluff.\n\n{journal_text}"
    }]
)
```

### Home screen suggestions
```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=400,
    messages=[{
        "role": "user",
        "content": f"Based on this data, give 3 short actionable suggestions for today. Direct tone, no softness. Return JSON array: [{{'title':'...','description':'...'}}]\n\nRecovery: {recovery}%\nHRV: {hrv}\nSleep: {sleep_hours}h\nKcal eaten: {kcal_today}\nProtein eaten: {protein_today}g\nProtein goal: {protein_goal}g"
    }]
)
```

---

## App screens

### Home
- Good morning greeting + current date
- Daily motivational quote (rotates daily, pulled from curated list of stoic/discipline quotes)
- Body vitals: Recovery %, Sleep duration, HRV — synced from Whoop
- "What to do today" — 3 AI-generated suggestions based on recovery + food data
- Morning check-in journal card — 4 questions, one at a time, step-by-step
- Weekly recap section (visible on Sundays or on demand)

### Food
- Kcal ring showing eaten vs goal
- Macro strip: Protein / Carbs / Fat
- Meal list with photo thumbnails
- "Log meal with photo" button → sheet → camera/upload → AI analysis → confirm → saved

### Sleep
- Big sleep duration display
- Sleep stage bar (awake / light / deep)
- Recovery score card with green/amber/red status
- HRV with week-over-week trend
- Two AI insight cards: today's recommendation + tomorrow's plan

---

## Design principles

- **Simple over feature-rich** — one action per screen
- **Direct copy** — "Don't waste this window." not "Great job, you're ready to train!"
- **No streaks** — discipline is not a game
- **Dark data, light surfaces** — no colored backgrounds, content breathes
- **Bebas Neue for impact** — numbers and headlines hit hard
- **Blue is the only accent** — no yellow, no orange, no gradients

---

## Quote pool (daily rotation)

Stoic and discipline-focused quotes from: Marcus Aurelius, Seneca, Epictetus, Bruce Lee, Arnold Schwarzenegger, Jim Rohn, Jerzy Gregorek, Henry Rollins, Confucius, Buddha. Rotates by day of month so it's consistent but changes daily.

---

## Build order

1. Django project setup + PostgreSQL + auth
2. Journal model + API endpoints + save to DB
3. Meal photo upload + Claude Vision analysis endpoint
4. PWA manifest + service worker (installable on phone)
5. Connect HTML frontend to Django REST API
6. Whoop OAuth2 flow + sync endpoint
7. Claude weekly recap generation (triggered Sunday)
8. Claude home screen suggestions (based on live data)
9. Push notifications (morning journal reminder, weekly recap)
10. Production deploy via Railway + Terraform

---

## Project context

Built by a final-year HvA Software Engineering student as a graduation project. Stack: Django, PostgreSQL, Python, TypeScript-ready frontend, Terraform for infra. The app is also a strong thesis candidate framed as: *"AI-assisted behavioral pattern recognition through multimodal daily logging in men's health."*

App name: **Monk**
Tagline: **Built for men who don't miss days**
Pillars: **Mind. Body. Rest.**