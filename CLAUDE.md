# Monk — Mind. Body. Rest.

> Built for men who don't miss days.

---

## Wat is Monk?

Monk is een men's health app die AI-powered food tracking, wearable data (Whoop / Apple Health), en een dagelijks journal combineert in één gefocuste ervaring. Het doel: open de app 's ochtends, weet wat je moet doen, sluit de app en voer het uit.

Geen ruis. Geen gamification. Geen streaks. Alleen data en discipline.

---

## De drie pijlers

- **Mind** — Dagelijks journal met 4 vragen. Elke zondag een AI-gegenereerde weekrecap.
- **Body** — Foto van je maaltijd → Claude Vision analyseert → kcal + macros automatisch gelogd.
- **Rest** — Whoop of Apple Health sync. Slaap, HRV, recovery score, AI-suggesties.

---

## Projectstructuur

```
monk/
├── frontend/                  # PWA — HTML + vanilla JS
│   ├── index.html             # Hoofd app shell
│   ├── manifest.json          # PWA installeerbaar maken
│   ├── sw.js                  # Service worker (offline)
│   ├── app.js                 # Navigatie + state
│   └── screens/
│       ├── home.js            # Home screen (quote, vitals, journal, suggesties)
│       ├── food.js            # Food log + foto upload
│       └── sleep.js           # Sleep & recovery
│
├── backend/                   # Django REST API
│   ├── manage.py
│   ├── monk/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       ├── journal/           # JournalEntry model + views
│       │   ├── models.py
│       │   ├── views.py
│       │   ├── urls.py
│       │   └── serializers.py
│       ├── food/              # Meal model + Claude Vision analyse
│       │   ├── models.py
│       │   ├── views.py
│       │   ├── urls.py
│       │   └── serializers.py
│       └── health/            # DailyHealth + Whoop sync
│           ├── models.py
│           ├── views.py
│           └── urls.py
│
├── services/                  # Gedeelde business logic
│   ├── claude.py              # Alle Claude API calls
│   ├── whoop.py               # Whoop REST API + OAuth
│   ├── health.py              # Apple HealthKit bridge
│   └── recap.py               # Weekly recap generatie (Celery task)
│
├── infra/                     # Terraform
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── railway.tf
│   ├── db.tf
│   └── dns.tf
│
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

---

## Tech stack

| Laag | Technologie |
|------|-------------|
| Frontend | HTML, vanilla TypeScript, CSS |
| PWA | manifest.json + service worker |
| Backend | Django 5 + Django REST Framework |
| Database | PostgreSQL |
| Auth | Django Allauth (OAuth2 voor Whoop) |
| AI | Anthropic Python SDK — claude-sonnet-4-6 |
| Queue | Celery + Redis (weekly recap, sync taken) |
| Storage | S3-compatible (maaltijd foto's) |
| Infra | Terraform naar Railway |
| Extern | Whoop API, Apple HealthKit |

### Design regels (niet aanpassen)
- Accent kleur: #1A6FD4 (steel blue), #0C4A9E (navy)
- Geen geel. Geen oranje. Geen gradients.
- Fonts: Bebas Neue (headlines/getallen), Barlow (body/UI)
- Copy: direct en bot. "Don't waste this window." niet "Great job!"

---

## Database modellen

```python
# apps/journal/models.py
class JournalEntry(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    date        = models.DateField(auto_now_add=True)
    answer_1    = models.TextField()   # Wat wil je vandaag bereiken?
    answer_2    = models.TextField()   # Hoe is je energie en mindset?
    answer_3    = models.TextField()   # Wat maakt vandaag een overwinning?
    answer_4    = models.TextField()   # Waar ben je dankbaar voor?
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']


# apps/food/models.py
class Meal(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    name        = models.CharField(max_length=200)
    kcal        = models.IntegerField()
    protein_g   = models.FloatField()
    carbs_g     = models.FloatField()
    fat_g       = models.FloatField()
    photo       = models.ImageField(upload_to='meals/%Y/%m/%d/')
    logged_at   = models.DateTimeField(auto_now_add=True)


# apps/journal/models.py
class WeeklyRecap(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start      = models.DateField()
    ai_summary      = models.TextField()
    generated_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'week_start']


# apps/health/models.py
class DailyHealth(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    date                = models.DateField()
    recovery_score      = models.FloatField(null=True)
    hrv                 = models.FloatField(null=True)
    sleep_hours         = models.FloatField(null=True)
    deep_sleep_pct      = models.FloatField(null=True)
    steps               = models.IntegerField(null=True)
    source              = models.CharField(max_length=20)  # 'whoop' of 'apple'

    class Meta:
        unique_together = ['user', 'date']


class WhoopToken(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token    = models.TextField()
    refresh_token   = models.TextField()
    expires_at      = models.DateTimeField()
```

---

## API endpoints

| Method | Endpoint | Wat het doet |
|--------|----------|--------------|
| POST | /api/meals/analyze/ | Foto uploaden → Claude → kcal + macros terug |
| POST | /api/meals/ | Maaltijd opslaan in database |
| GET | /api/meals/today/ | Alle maaltijden van vandaag + totaal kcal |
| POST | /api/journal/ | Dagelijks journal opslaan |
| GET | /api/journal/week/ | De 7 entries van deze week ophalen |
| POST | /api/journal/recap/ | Claude weekrecap handmatig triggeren |
| GET | /api/whoop/sync/ | Whoop data ophalen en opslaan in DailyHealth |
| GET | /api/health/today/ | Geaggregeerde gezondheidsdata voor home screen |
| GET | /api/health/suggestions/ | Claude AI-suggesties voor vandaag |

---

## Claude API gebruik

### Maaltijd foto analyseren
```python
# services/claude.py
import anthropic, base64, json

client = anthropic.Anthropic()

def analyze_meal_photo(image_bytes: bytes, media_type: str) -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=250,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": b64}
                },
                {
                    "type": "text",
                    "text": 'Analyze this food photo. Reply ONLY with JSON, no backticks: {"name":"...","kcal":0,"protein_g":0,"carbs_g":0,"fat_g":0}'
                }
            ]
        }]
    )
    return json.loads(message.content[0].text)
```

### Weekrecap genereren
```python
def generate_weekly_recap(entries: list) -> str:
    journal_text = "\n\n".join([
        f"{e.date}:\n"
        f"- Doel: {e.answer_1}\n"
        f"- Energie: {e.answer_2}\n"
        f"- Overwinning: {e.answer_3}\n"
        f"- Dankbaar: {e.answer_4}"
        for e in entries
    ])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                "You are a direct, no-nonsense coach writing a weekly recap for a man. "
                "Based on his journal entries below, write 3-4 sentences. "
                "Be honest, specific, mention patterns you notice. No fluff, no softness.\n\n"
                + journal_text
            )
        }]
    )
    return message.content[0].text
```

### Home screen suggesties
```python
def generate_suggestions(recovery: float, hrv: float, sleep_h: float,
                          kcal_today: int, protein_today: float) -> list:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": (
                "Give 3 short actionable suggestions for today. Direct tone, no softness. "
                'Return ONLY a JSON array: [{"title":"...","description":"..."}]\n\n'
                f"Recovery: {recovery}%\nHRV: {hrv}\nSleep: {sleep_h}h\n"
                f"Kcal eaten: {kcal_today}\nProtein eaten: {protein_today}g"
            )
        }]
    )
    return json.loads(message.content[0].text)
```

---

## Whoop integratie

```python
# services/whoop.py
import requests

WHOOP_BASE = "https://api.prod.whoop.com/developer/v1"

def get_today_data(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}

    recovery = requests.get(f"{WHOOP_BASE}/recovery", headers=headers).json()
    sleep    = requests.get(f"{WHOOP_BASE}/activity/sleep", headers=headers).json()

    rec = recovery["records"][0] if recovery.get("records") else {}
    slp = sleep["records"][0]    if sleep.get("records")    else {}

    return {
        "recovery_score": rec.get("score", {}).get("recovery_score"),
        "hrv":            rec.get("score", {}).get("hrv_rmssd_milli"),
        "sleep_hours":    slp.get("score", {}).get("total_in_bed_time_milli", 0) / 3_600_000,
        "source":         "whoop",
    }
```

OAuth2 flow: registreer app op developer.whoop.com, stel Django Allauth in met SOCIALACCOUNT_PROVIDERS, tokens opslaan in WhoopToken model.

---

## Architectuur

```
[Monk PWA — HTML/JS]
        |
        | HTTPS REST
        v
[Django REST API — Railway]
        |
        |-- [PostgreSQL] — alle data
        |-- [S3 Storage] — maaltijd foto's
        |-- [Claude API] — foto analyse, recap, suggesties
        |-- [Whoop API]  — recovery, HRV, slaap
        |-- [Celery + Redis] — achtergrond taken
        |
[Terraform] — Railway, DB, Redis, DNS
```

---

## Flow — maaltijd loggen

```
1. PWA stuurt POST /api/meals/analyze/ met foto
2. Django leest image bytes
3. services/claude.py stuurt base64 naar Claude Vision
4. Claude geeft terug: { name, kcal, protein_g, carbs_g, fat_g }
5. Django slaat Meal op in PostgreSQL
6. Response naar PWA — kcal ring updaten
```

## Flow — weekly recap (zondag automatisch)

```
1. Celery beat triggert elke zondag om 20:00
2. recap.py haalt 7 JournalEntry records op
3. services/claude.py stuurt entries naar Claude
4. Claude schrijft 3-4 zinnen coaching recap
5. WeeklyRecap opgeslagen in PostgreSQL
6. Volgende app open — recap zichtbaar op home screen
```

## Flow — Whoop sync

```
1. PWA of Celery task roept GET /api/whoop/sync/ aan
2. Django haalt WhoopToken op voor user
3. services/whoop.py vraagt recovery + sleep op bij Whoop API
4. Data opgeslagen in DailyHealth model
5. Claude genereert suggesties op basis van nieuwe data
6. Home screen toont actuele recovery, HRV, slaap
```

---

## Environment variables

```bash
# .env — nooit committen naar git
SECRET_KEY=django-secret-key-hier
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/monk
ANTHROPIC_API_KEY=sk-ant-...
WHOOP_CLIENT_ID=...
WHOOP_CLIENT_SECRET=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=monk-media
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=monk.app,www.monk.app
```

---

## Bouwvolgorde

1. Django project opzetten + PostgreSQL + basis auth
2. Journal app — model, views, serializers, endpoints
3. Food app — Meal model + Claude Vision analyse endpoint
4. Health app — DailyHealth model + Whoop OAuth + sync
5. Services laag — claude.py, whoop.py, recap.py
6. Celery + Redis — background taken instellen
7. PWA frontend — manifest.json + service worker
8. Frontend koppelen aan Django API
9. Terraform — Railway deployment configureren
10. Productie deploy + testen op echte telefoon

---

## Projectcontext

Gebouwd door een afstuderende HvA Software Engineering student als graduation project.

App naam: Monk
Tagline: Built for men who don't miss days
Pijlers: Mind, Body, Rest
Thesis framing: AI-assisted behavioral pattern recognition through multimodal daily logging in men's health

Stack die je al kent: Django, PostgreSQL, Python, TypeScript, HTML, Terraform

Werkend prototype: forge_app.html — volledig werkende HTML/JS demo met Claude API integratie al ingebouwd