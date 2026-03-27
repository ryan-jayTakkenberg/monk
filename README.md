# Monk — Mind. Body. Rest.

> Built for men who don't miss days.

A men's health PWA that combines AI-powered food tracking, wearable recovery data (Whoop), and a daily journal into one focused experience.

---

## Stack

### Frontend
- **React 18 + TypeScript** — component-based UI
- **Vite** — build tool and dev server
- **vite-plugin-pwa** — service worker and PWA manifest generation
- Fonts: Bebas Neue (headlines/numbers), Barlow (body/UI)

### Backend
- **Django 5 + Django REST Framework** — REST API
- **PostgreSQL** — primary database
- **SimpleJWT** — JWT authentication
- **Django Allauth** — OAuth2 flow for Whoop
- **Anthropic Python SDK** — Claude API (food analysis, journal recap, daily suggestions)
- **Pillow** — meal photo handling

### Deploy
- **Railway** — Django backend + PostgreSQL
- **Vercel** — React frontend

---

## Project structure

```
monk/
├── frontend/          # React + TypeScript + Vite PWA
│   ├── src/
│   │   ├── screens/   # Home, Food, Sleep
│   │   ├── components/
│   │   ├── api/       # API client (typed fetch wrappers)
│   │   └── types/
│   └── vite.config.ts
└── backend/           # Django REST API
    ├── apps/
    │   ├── journal/   # JournalEntry, WeeklyRecap
    │   ├── food/      # Meal, photo upload, Claude Vision
    │   └── health/    # WhoopToken, sleep + recovery sync
    ├── monk/          # Django project settings
    └── requirements.txt
```

---

## External APIs

| API | Purpose |
|-----|---------|
| Anthropic Claude (`claude-sonnet-4-6`) | Food photo analysis, weekly journal recap, daily suggestions |
| Whoop REST API (`api.prod.whoop.com/developer/v1/`) | Recovery score, HRV, sleep stages |

---

## Getting started

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python3 manage.py migrate
python3 manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
