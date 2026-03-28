"""
python manage.py seed                     # demo user, 7 days of data
python manage.py seed --user ryan         # specific user (created if missing)
python manage.py seed --days 14           # more history
python manage.py seed --clear             # wipe existing data first
python manage.py seed --user ryan --clear --days 14
"""
import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.food.models import Meal
from apps.health.models import WhoopSleepRecord, WhoopToken
from apps.journal.models import JournalEntry, WeeklyRecap


# ── Data pools ────────────────────────────────────────────────────────────────

MEALS = [
    # (name, kcal, protein_g, carbs_g, fat_g)
    ("Scrambled eggs + toast",         420, 28, 34,  14),
    ("Greek yoghurt + granola",         350, 18, 42,   8),
    ("Oatmeal + banana + protein",      480, 35, 58,   9),
    ("Chicken breast + rice + broccoli",580, 52, 48,   8),
    ("Tuna wrap",                       430, 38, 36,   9),
    ("Steak + sweet potato",            620, 48, 44,  16),
    ("Salmon + quinoa + spinach",       540, 44, 38,  14),
    ("Protein shake + almonds",         340, 32, 18,  12),
    ("Cottage cheese + fruit",          280, 24, 26,   4),
    ("Ground beef bowl + rice",         590, 46, 52,  14),
    ("Pasta bolognese",                 680, 38, 74,  16),
    ("Avocado toast + eggs",            490, 22, 42,  22),
    ("Beef stir fry + noodles",         610, 42, 58,  14),
    ("Protein pancakes",                420, 34, 44,   8),
    ("Chicken Caesar salad",            480, 40, 18,  24),
    ("Whey shake + banana",             320, 30, 36,   4),
    ("Nuts + dark chocolate",           280, 8,  18,  20),
    ("Rice cakes + peanut butter",      260, 8,  30,  10),
]

JOURNAL_ANSWERS = [
    {
        "a1": "Finish the backend API and push to staging.",
        "a2": "Energy is solid — slept 7.5h, feel sharp.",
        "a3": "Deploying without bugs and hitting 180g protein.",
        "a4": "Grateful for the discipline that got me here.",
    },
    {
        "a1": "Complete the frontend food log screen.",
        "a2": "A bit sluggish, coffee helped. Mindset is locked in.",
        "a3": "Getting one full feature shipped end-to-end.",
        "a4": "Grateful for a working setup and clear goals.",
    },
    {
        "a1": "Write 1000 words of the thesis methodology.",
        "a2": "Good energy, HRV was high this morning.",
        "a3": "Making real progress on the thesis — even 500 words counts.",
        "a4": "Grateful for the project and the skills it's building.",
    },
    {
        "a1": "Train legs and hit all accessory work.",
        "a2": "Legs day dread is real but the mind is willing.",
        "a3": "Completing the workout without skipping sets.",
        "a4": "Grateful for a healthy body that can train hard.",
    },
    {
        "a1": "Refactor the Whoop sync service and write tests.",
        "a2": "Slightly tired but focused. No distractions today.",
        "a3": "Clean code pushed — tests green.",
        "a4": "Grateful for the momentum I've built this week.",
    },
    {
        "a1": "Deep work session: Celery setup + Redis config.",
        "a2": "High energy. Slept 8h. Ready to ship.",
        "a3": "Background tasks running reliably.",
        "a4": "Grateful for the tools that make this possible.",
    },
    {
        "a1": "Rest day — walk, read, plan next week.",
        "a2": "Calm and recovered. Body needed this.",
        "a3": "Actually resting without guilt.",
        "a4": "Grateful for rest as part of the process.",
    },
]

WEEKLY_RECAPS = [
    "You showed up every day this week — that's the baseline, not the ceiling. "
    "Energy was inconsistent early on but you course-corrected fast. "
    "Protein hit 170g+ on 5 of 7 days. Next week: fix the sleep window.",

    "Mixed week. You let two mornings slip without a journal entry — that pattern "
    "always precedes lower output days. Training was consistent. "
    "The thesis work needs a dedicated block, not leftover time.",

    "Strong week. Recovery scores trended up after you cut the late screens. "
    "You hit your focus goal 6 out of 7 days. "
    "One thing: stop skipping the gratitude question — it's not soft, it's data.",
]


# ── Command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Seed the database with realistic mock data for development."

    def add_arguments(self, parser):
        parser.add_argument("--user",  default="demo",  help="Username (created if missing)")
        parser.add_argument("--days",  default=7, type=int, help="Days of history to generate")
        parser.add_argument("--clear", action="store_true", help="Delete existing seed data first")

    def handle(self, *args, **options):
        username = options["user"]
        days     = options["days"]
        clear    = options["clear"]

        # ── User ──────────────────────────────────────────────────────────────
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@monk.local", "first_name": username.capitalize()},
        )
        user.set_password("demo")
        user.save()
        self.stdout.write(f"  {'Created' if created else 'Updated'} user '{username}' (password: demo)")

        # ── Clear ─────────────────────────────────────────────────────────────
        if clear:
            WhoopSleepRecord.objects.filter(user=user).delete()
            Meal.objects.filter(user=user).delete()
            JournalEntry.objects.filter(user=user).delete()
            WeeklyRecap.objects.filter(user=user).delete()
            WhoopToken.objects.filter(user=user).delete()
            self.stdout.write("  Cleared existing data.")

        today = date.today()

        # ── Whoop token (fake — marks device as connected) ────────────────────
        WhoopToken.objects.get_or_create(
            user=user,
            defaults={
                "access_token":  "mock_access_token",
                "refresh_token": "mock_refresh_token",
                "expires_at":    timezone.now() + timedelta(days=365),
            },
        )

        # ── Sleep / recovery records ──────────────────────────────────────────
        sleep_created = 0
        for i in range(days):
            day = today - timedelta(days=i)

            # Realistic variation: recovery cycles between good/average/bad weeks
            base_recovery = 75 - (i % 7) * 3
            recovery = max(20, min(99, base_recovery + random.randint(-8, 8)))
            hrv      = round(40 + recovery * 0.45 + random.uniform(-5, 5), 1)
            sleep_h  = round(6.5 + random.uniform(-0.8, 1.4), 2)

            # Sleep stage split roughly: awake 5%, light 45%, deep 50%
            awake = round(random.uniform(3, 8), 1)
            deep  = round(random.uniform(18, 35), 1)
            light = round(100 - awake - deep, 1)

            _, c = WhoopSleepRecord.objects.update_or_create(
                user=user,
                recorded_date=day,
                defaults={
                    "duration_hours": sleep_h,
                    "recovery_score": recovery,
                    "hrv":            hrv,
                    "awake_pct":      awake,
                    "light_pct":      light,
                    "deep_pct":       deep,
                },
            )
            if c:
                sleep_created += 1

        self.stdout.write(f"  Sleep records: {sleep_created} created ({days} total)")

        # ── Meals (2–4 per day) ───────────────────────────────────────────────
        meals_created = 0
        for i in range(days):
            day = today - timedelta(days=i)
            daily_meals = random.sample(MEALS, random.randint(2, 4))
            for meal_data in daily_meals:
                name, kcal, prot, carbs, fat = meal_data
                # Small daily variation so totals aren't identical
                m = Meal(
                    user=user,
                    name=name,
                    kcal=kcal + random.randint(-20, 20),
                    protein_g=round(prot + random.uniform(-2, 2), 1),
                    carbs_g=round(carbs + random.uniform(-3, 3), 1),
                    fat_g=round(fat + random.uniform(-1, 1), 1),
                )
                m.save()
                # Backdate logged_at to the correct day
                Meal.objects.filter(pk=m.pk).update(
                    logged_at=timezone.make_aware(
                        timezone.datetime(day.year, day.month, day.day,
                                          random.randint(7, 20), random.randint(0, 59))
                    )
                )
                meals_created += 1

        self.stdout.write(f"  Meals: {meals_created} created")

        # ── Journal entries ───────────────────────────────────────────────────
        journal_created = 0
        for i in range(days):
            day = today - timedelta(days=i)
            answers = JOURNAL_ANSWERS[i % len(JOURNAL_ANSWERS)]
            _, c = JournalEntry.objects.get_or_create(
                user=user,
                date=day,
                defaults={
                    "answer_1": answers["a1"],
                    "answer_2": answers["a2"],
                    "answer_3": answers["a3"],
                    "answer_4": answers["a4"],
                },
            )
            if c:
                journal_created += 1

        self.stdout.write(f"  Journal entries: {journal_created} created")

        # ── Weekly recap (current week) ───────────────────────────────────────
        week_start = today - timedelta(days=today.weekday())
        recap_text = random.choice(WEEKLY_RECAPS)
        _, c = WeeklyRecap.objects.get_or_create(
            user=user,
            week_start=week_start,
            defaults={"ai_summary": recap_text},
        )
        self.stdout.write(f"  Weekly recap: {'created' if c else 'already exists'}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Login → username: {username}  password: demo"
        ))
