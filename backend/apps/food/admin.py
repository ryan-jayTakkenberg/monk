from django.contrib import admin
from .models import Meal, UserFoodSettings


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display  = ('user', 'name', 'kcal', 'protein_g', 'carbs_g', 'fat_g', 'logged_at')
    list_filter   = ('logged_at', 'user')
    search_fields = ('user__username', 'name')
    ordering      = ('-logged_at',)
    readonly_fields = ('logged_at',)

    fieldsets = (
        (None, {'fields': ('user', 'name', 'photo')}),
        ('Macros', {'fields': ('kcal', 'protein_g', 'carbs_g', 'fat_g')}),
        ('Meta', {'fields': ('logged_at',)}),
    )


@admin.register(UserFoodSettings)
class UserFoodSettingsAdmin(admin.ModelAdmin):
    list_display  = ('user', 'kcal_goal', 'protein_goal_g')
    search_fields = ('user__username',)
