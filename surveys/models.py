from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Survey(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название опроса")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        db_table = 'surveys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"

    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Опрос"
    )
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Порядок отображения"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'questions'
        ordering = ['survey', 'order']
        indexes = [
            models.Index(fields=['survey', 'order']),
        ]
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        unique_together = ['survey', 'order']

    def __str__(self):
        return f"{self.survey.title} - Q{self.order}: {self.text[:50]}"


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer_options',
        verbose_name="Вопрос"
    )
    text = models.CharField(max_length=500, verbose_name="Текст варианта ответа")
    order = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Порядок отображения"
    )

    class Meta:
        db_table = 'answer_options'
        ordering = ['question', 'order']
        indexes = [
            models.Index(fields=['question', 'order']),
        ]
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"
        unique_together = ['question', 'order']

    def __str__(self):
        return f"{self.question.text[:30]} - A{self.order}: {self.text}"


class SurveyResponse(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="Опрос"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='survey_responses',
        verbose_name="Пользователь"
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Начало прохождения")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Завершение прохождения")
    is_completed = models.BooleanField(default=False, verbose_name="Завершен")

    class Meta:
        db_table = 'survey_responses'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['survey', 'user']),
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['survey', 'is_completed']),
        ]
        verbose_name = "Прохождение опроса"
        verbose_name_plural = "Прохождения опросов"
        unique_together = ['survey', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.survey.title}"


class Answer(models.Model):
    survey_response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Прохождение опроса"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Вопрос"
    )
    answer_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Выбранный вариант"
    )
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Время ответа")

    class Meta:
        db_table = 'answers'
        ordering = ['survey_response', 'question__order']
        indexes = [
            models.Index(fields=['survey_response', 'question']),
            models.Index(fields=['question', 'answer_option']),
            models.Index(fields=['answer_option']),
        ]
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        unique_together = ['survey_response', 'question']

    def __str__(self):
        return f"{self.survey_response.user.username} - {self.question.text[:30]}: {self.answer_option.text}"