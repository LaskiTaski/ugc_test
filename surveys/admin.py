from django.contrib import admin
from .models import Survey, Question, AnswerOption, SurveyResponse, Answer


class AnswerOptionInline(admin.TabularInline):
    """Варианты ответов"""
    model = AnswerOption
    extra = 3
    ordering = ['order']


class QuestionInline(admin.TabularInline):
    """Вопросы"""
    model = Question
    extra = 1
    ordering = ['order']
    show_change_link = True


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """Опросы"""
    list_display = ['title', 'author', 'created_at', 'is_active', 'questions_count']
    list_filter = ['is_active', 'created_at', 'author']
    search_fields = ['title', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionInline]

    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = 'Количество вопросов'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Вопросы"""
    list_display = ['text_preview', 'survey', 'order', 'created_at']
    list_filter = ['survey', 'created_at']
    search_fields = ['text', 'survey__title']
    inlines = [AnswerOptionInline]
    ordering = ['survey', 'order']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст вопроса'


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    """Варианты ответов"""
    list_display = ['text', 'question_preview', 'order']
    list_filter = ['question__survey']
    search_fields = ['text', 'question__text']
    ordering = ['question', 'order']

    def question_preview(self, obj):
        return obj.question.text[:30] + '...' if len(obj.question.text) > 30 else obj.question.text
    question_preview.short_description = 'Вопрос'


class AnswerInline(admin.TabularInline):
    """Ответы"""
    model = Answer
    extra = 0
    readonly_fields = ['question', 'answer_option', 'answered_at']
    can_delete = False


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    """Прохождения опросов"""
    list_display = ['user', 'survey', 'started_at', 'completed_at', 'is_completed']
    list_filter = ['is_completed', 'survey', 'started_at']
    search_fields = ['user__username', 'survey__title']
    readonly_fields = ['started_at', 'completed_at']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Ответы пользователей"""
    list_display = ['user_name', 'question_preview', 'answer_option', 'answered_at']
    list_filter = ['survey_response__survey', 'answered_at']
    search_fields = ['survey_response__user__username', 'question__text']
    readonly_fields = ['answered_at']

    def user_name(self, obj):
        return obj.survey_response.user.username
    user_name.short_description = 'Пользователь'

    def question_preview(self, obj):
        return obj.question.text[:30] + '...' if len(obj.question.text) > 30 else obj.question.text
    question_preview.short_description = 'Вопрос'