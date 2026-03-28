from django.contrib import admin
from .models import JournalEntry, WeeklyRecap


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display  = ('user', 'date', 'answer_1_preview', 'answer_2_preview', 'created_at')
    list_filter   = ('date', 'user')
    search_fields = ('user__username', 'answer_1', 'answer_2', 'answer_3', 'answer_4')
    ordering      = ('-date',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {'fields': ('user', 'date')}),
        ('Journal answers', {'fields': ('answer_1', 'answer_2', 'answer_3', 'answer_4')}),
        ('Meta', {'fields': ('created_at',)}),
    )

    def answer_1_preview(self, obj):
        return obj.answer_1[:60] + '…' if len(obj.answer_1) > 60 else obj.answer_1
    answer_1_preview.short_description = 'Focus'

    def answer_2_preview(self, obj):
        return obj.answer_2[:60] + '…' if len(obj.answer_2) > 60 else obj.answer_2
    answer_2_preview.short_description = 'Energy'


@admin.register(WeeklyRecap)
class WeeklyRecapAdmin(admin.ModelAdmin):
    list_display  = ('user', 'week_start', 'summary_preview', 'generated_at')
    list_filter   = ('week_start', 'user')
    search_fields = ('user__username', 'ai_summary')
    ordering      = ('-week_start',)
    readonly_fields = ('generated_at',)

    def summary_preview(self, obj):
        return obj.ai_summary[:100] + '…' if len(obj.ai_summary) > 100 else obj.ai_summary
    summary_preview.short_description = 'AI Summary'
