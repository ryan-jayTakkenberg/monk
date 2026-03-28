from django.contrib import admin
from .models import WhoopToken, WhoopSleepRecord


@admin.register(WhoopSleepRecord)
class WhoopSleepRecordAdmin(admin.ModelAdmin):
    list_display  = ('user', 'recorded_date', 'recovery_score', 'hrv', 'duration_hours', 'deep_pct', 'synced_at')
    list_filter   = ('recorded_date', 'user')
    search_fields = ('user__username',)
    ordering      = ('-recorded_date',)
    readonly_fields = ('synced_at',)

    fieldsets = (
        (None, {'fields': ('user', 'recorded_date')}),
        ('Recovery', {'fields': ('recovery_score', 'hrv')}),
        ('Sleep', {'fields': ('duration_hours', 'awake_pct', 'light_pct', 'deep_pct')}),
        ('Meta', {'fields': ('synced_at',)}),
    )


@admin.register(WhoopToken)
class WhoopTokenAdmin(admin.ModelAdmin):
    list_display  = ('user', 'expires_at')
    search_fields = ('user__username',)
    readonly_fields = ('access_token', 'refresh_token', 'expires_at')
