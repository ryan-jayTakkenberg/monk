# Monk — Open Issues

> Bijgehouden per workstream. Vink af met [x] zodra iets klaar is.

---

## Backend

### Auth
- [ ] **MONK-001** Whoop OAuth2 flow — redirect naar `developer.whoop.com`, callback endpoint, tokens opslaan in `WhoopToken`
- [ ] **MONK-002** Token refresh voor Whoop — access token automatisch vernieuwen als `expires_at` verstreken is
- [ ] **MONK-003** Password reset endpoint (`POST /api/auth/password/reset/`)

### Journal
- [ ] **MONK-004** Weekly recap automatisch triggeren elke zondag (Celery beat task)
- [ ] **MONK-005** `GET /api/journal/recap/history/` — lijst van alle vorige recaps

### Food
- [x] **MONK-006** `DELETE /api/meals/<id>/` — maaltijd verwijderen
- [ ] **MONK-007** Dagelijks kcal doel instelbaar per user (nu hardcoded 2000)
- [ ] **MONK-008** Fout afhandelen als Claude geen geldig JSON teruggeeft bij foto analyse — retry 1x, daarna 400

### Health / Whoop
- [ ] **MONK-009** Whoop sync automatiseren via Celery (elke nacht om 06:00)
- [ ] **MONK-010** Apple HealthKit fallback — `POST /api/health/apple/` om data te ontvangen als geen Whoop
- [ ] **MONK-011** `GET /api/health/history/` — slaap + recovery van de afgelopen 7 dagen

### Services laag
- [ ] **MONK-012** `backend/services/claude.py` aanmaken — alle Claude calls uit views knippen en centraliseren
- [ ] **MONK-013** `backend/services/whoop.py` aanmaken — Whoop API calls centraliseren
- [ ] **MONK-014** `backend/services/recap.py` aanmaken — Celery task voor weekrecap

### Infrastructuur
- [ ] **MONK-015** Celery + Redis installeren en configureren (`requirements.txt`, `settings.py`, `celery.py`)
- [ ] **MONK-016** S3 storage configureren voor maaltijd foto's (nu gaan ze naar lokale schijf)
- [ ] **MONK-017** Serializers toevoegen per app (`serializers.py`) — views opschonen

---

## Frontend

### Home screen
- [x] **MONK-018** Dagelijkse quote tonen (roteert op datum, uit geselecteerde pool van stoïcijnse quotes)
- [ ] **MONK-019** Whoop vitals tonen op home (recovery %, slaap uur, HRV) — compact bovenaan
- [ ] **MONK-020** Weekly recap tonen op zondag automatisch zonder knop

### Food screen
- [ ] **MONK-021** Maaltijd verwijderen — swipe of knop per rij
- [ ] **MONK-022** Kcal doel instelbaar maken via instellingen scherm

### Sleep screen
- [ ] **MONK-023** Slaap geschiedenis grafiek — 7 dagen bar chart
- [ ] **MONK-024** AI insight kaart — "wat betekent je recovery vandaag, wat te doen"

### Algemeen
- [x] **MONK-025** Settings scherm — username tonen, uitloggen, kcal doel aanpassen
- [ ] **MONK-026** PWA icons toevoegen (`public/icons/icon-192.png` en `icon-512.png`) — app is nu niet installeerbaar
- [ ] **MONK-027** Offline fallback pagina — service worker toont melding als geen internet
- [ ] **MONK-028** Loading skeletons vervangen door echte loading states (nu returns leeg scherm)

---

## Deploy

- [x] **MONK-029** `Procfile` aanmaken — `web: gunicorn monk.wsgi:application`
- [x] **MONK-030** `whitenoise` toevoegen aan requirements voor static files
- [ ] **MONK-031** Railway project aanmaken + PostgreSQL addon koppelen
- [ ] **MONK-032** Environment variables instellen op Railway (zie `deploy-engineer` agent)
- [ ] **MONK-033** Frontend build deployen (Railway static of Vercel)
- [ ] **MONK-034** `infra/` map aanmaken met Terraform config voor Railway + DB + Redis + DNS
- [ ] **MONK-035** CI/CD pipeline — GitHub Actions: test + deploy bij push naar `main`

---

## Security

- [x] **MONK-036** File size limiet op foto uploads — weiger > 10MB
- [x] **MONK-037** Valideer `content_type` van uploads — alleen `image/*` accepteren
- [ ] **MONK-038** `SECRET_KEY` genereren met `secrets.token_hex(32)` en in Railway zetten
- [ ] **MONK-039** `DEBUG=False` + `ALLOWED_HOSTS` instellen voor productie
- [ ] **MONK-040** Rate limiting op `/api/auth/token/` — voorkom brute force login
- [ ] **MONK-041** `.env` controleren — nooit committen (`.gitignore` staat er, dubbelchecken)

---

## Afstuderen / Thesis

- [ ] **MONK-042** README bijwerken met installatie instructies en screenshots
- [ ] **MONK-043** API documentatie — Swagger/OpenAPI via `drf-spectacular`
- [ ] **MONK-044** Werkend prototype testen op echte iPhone (PWA installeren)
- [ ] **MONK-045** Thesis sectie: "AI-assisted behavioral pattern recognition through multimodal daily logging"

---

## Overzicht

| Workstream | Totaal | Klaar |
|------------|--------|-------|
| Backend | 17 | 0 |
| Frontend | 11 | 0 |
| Deploy | 7 | 0 |
| Security | 6 | 0 |
| Thesis | 4 | 0 |
| **Totaal** | **45** | **0** |
