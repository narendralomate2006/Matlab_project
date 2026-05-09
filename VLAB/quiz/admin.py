from django.contrib import admin
from .models import Question, Test, TestAttempt

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'type', 'subject', 'correct_answer')
    list_filter = ('type', 'subject')
    search_fields = ('text', 'correct_answer')

    def text_preview(self, obj):
        return obj.text[:50]
    text_preview.short_description = 'Question Text'

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_minutes', 'question_count')
    filter_horizontal = ('questions',)

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Total Questions'

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'time_taken_seconds', 'completed_at')
    list_filter = ('test', 'completed_at')
    readonly_fields = ('completed_at',)
