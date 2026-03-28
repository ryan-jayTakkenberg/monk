from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Sum
from .models import Meal, UserFoodSettings
from services.claude import analyze_meal_photo
import json


class MealAnalyzeView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'No photo provided.'}, status=status.HTTP_400_BAD_REQUEST)

        allowed_content_types = {'image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif'}
        if photo.content_type not in allowed_content_types:
            return Response({'error': 'Invalid file type. Upload a photo.'}, status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024
        if photo.size > max_size:
            return Response({'error': 'Photo too large. Maximum 10MB.'}, status=status.HTTP_400_BAD_REQUEST)

        image_bytes = photo.read()
        media_type = photo.content_type or 'image/jpeg'

        try:
            result = analyze_meal_photo(image_bytes, media_type)
            return Response(result)
        except (json.JSONDecodeError, ValueError, KeyError, IndexError):
            return Response(
                {'error': 'Could not analyze photo. Try again.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
        food_settings, _ = UserFoodSettings.objects.get_or_create(user=request.user)
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
            },
            'kcal_goal': food_settings.kcal_goal,
            'protein_goal_g': food_settings.protein_goal_g,
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


class MealDetailView(APIView):
    def delete(self, request, pk):
        meal = Meal.objects.filter(pk=pk, user=request.user).first()
        if not meal:
            return Response(status=status.HTTP_404_NOT_FOUND)
        meal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFoodSettingsView(APIView):
    def get(self, request):
        food_settings, _ = UserFoodSettings.objects.get_or_create(user=request.user)
        return Response({'kcal_goal': food_settings.kcal_goal, 'protein_goal_g': food_settings.protein_goal_g})

    def patch(self, request):
        food_settings, _ = UserFoodSettings.objects.get_or_create(user=request.user)
        if 'kcal_goal' in request.data:
            food_settings.kcal_goal = int(request.data['kcal_goal'])
        if 'protein_goal_g' in request.data:
            food_settings.protein_goal_g = int(request.data['protein_goal_g'])
        food_settings.save()
        return Response({'kcal_goal': food_settings.kcal_goal, 'protein_goal_g': food_settings.protein_goal_g})
