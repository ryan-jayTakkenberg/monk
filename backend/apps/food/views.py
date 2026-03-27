from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Sum
from django.conf import settings
from .models import Meal
import base64
import anthropic


class MealAnalyzeView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'No photo provided.'}, status=status.HTTP_400_BAD_REQUEST)

        image_data = base64.standard_b64encode(photo.read()).decode('utf-8')
        media_type = photo.content_type or 'image/jpeg'

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=250,
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': media_type,
                            'data': image_data,
                        },
                    },
                    {
                        'type': 'text',
                        'text': 'Analyze this food photo. Reply ONLY with JSON, no backticks: {"name":"...","kcal":0,"protein_g":0,"carbs_g":0,"fat_g":0}'
                    }
                ],
            }]
        )

        text = message.content[0].text.strip()
        import json
        result = json.loads(text)
        return Response(result)


class MealListView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        today = timezone.localdate()
        meals = Meal.objects.filter(user=request.user, logged_at__date=today)
        totals = meals.aggregate(
            total_kcal=Sum('kcal'),
            total_protein=Sum('protein_g'),
            total_carbs=Sum('carbs_g'),
            total_fat=Sum('fat_g'),
        )
        return Response({
            'meals': [{
                'id': m.id,
                'name': m.name,
                'kcal': m.kcal,
                'protein_g': m.protein_g,
                'carbs_g': m.carbs_g,
                'fat_g': m.fat_g,
                'photo': request.build_absolute_uri(m.photo.url) if m.photo else None,
                'logged_at': m.logged_at,
            } for m in meals],
            'totals': {
                'kcal': totals['total_kcal'] or 0,
                'protein_g': totals['total_protein'] or 0,
                'carbs_g': totals['total_carbs'] or 0,
                'fat_g': totals['total_fat'] or 0,
            }
        })

    def post(self, request):
        meal = Meal.objects.create(
            user=request.user,
            name=request.data.get('name', 'Unknown'),
            kcal=int(request.data.get('kcal', 0)),
            protein_g=float(request.data.get('protein_g', 0)),
            carbs_g=float(request.data.get('carbs_g', 0)),
            fat_g=float(request.data.get('fat_g', 0)),
            photo=request.FILES.get('photo'),
        )
        return Response({'id': meal.id, 'name': meal.name, 'kcal': meal.kcal}, status=status.HTTP_201_CREATED)
