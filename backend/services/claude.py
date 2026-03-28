import anthropic
import base64
import json
import re
from django.conf import settings


def _parse_json(raw: str) -> dict:
    text = re.sub(r'^```(?:json)?\s*', '', raw.strip(), flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text.strip())


def analyze_meal_photo(image_bytes: bytes, media_type: str) -> dict:
    """Analyze a meal photo and return {name, kcal, protein_g, carbs_g, fat_g}. Retries once on bad JSON."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    claude_messages = [{
        'role': 'user',
        'content': [
            {'type': 'image', 'source': {'type': 'base64', 'media_type': media_type, 'data': base64.standard_b64encode(image_bytes).decode()}},
            {'type': 'text', 'text': 'Analyze this food photo. Reply ONLY with JSON, no backticks: {"name":"...","kcal":0,"protein_g":0,"carbs_g":0,"fat_g":0}'}
        ],
    }]
    for attempt in range(2):
        msg = client.messages.create(model='claude-sonnet-4-6', max_tokens=250, messages=claude_messages)
        try:
            return _parse_json(msg.content[0].text)
        except (json.JSONDecodeError, ValueError, KeyError, IndexError):
            if attempt == 1:
                raise


def generate_weekly_recap(entries: list) -> str:
    """Generate a weekly recap from a list of JournalEntry objects."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    journal_text = '\n\n'.join([
        f'Date: {e.date}\nOne thing to accomplish: {e.answer_1}\nEnergy and mindset: {e.answer_2}\nWhat makes today a win: {e.answer_3}\nGratitude: {e.answer_4}'
        for e in entries
    ])
    msg = client.messages.create(
        model='claude-sonnet-4-6', max_tokens=300,
        messages=[{'role': 'user', 'content': (
            'You are a direct, no-nonsense coach writing a weekly recap for a man. '
            'Based on his journal entries below, write 3-4 sentences. '
            'Be honest, specific, mention patterns you notice. No fluff, no softness.\n\n' + journal_text
        )}]
    )
    return msg.content[0].text


def generate_suggestions(recovery, hrv, sleep_h, kcal_today, protein_today) -> list:
    """Generate 3 actionable suggestions. Returns list of {title, description}."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model='claude-sonnet-4-6', max_tokens=400,
        messages=[{'role': 'user', 'content': (
            'Give 3 short actionable suggestions for today. Direct tone, no softness. '
            'Return ONLY a JSON array: [{"title":"...","description":"..."}]\n\n'
            f'Recovery: {recovery}%\nHRV: {hrv}ms\nSleep: {sleep_h}h\n'
            f'Kcal eaten: {kcal_today}\nProtein eaten: {protein_today}g\nProtein goal: 180g'
        )}]
    )
    return _parse_json(msg.content[0].text)
