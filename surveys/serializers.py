from rest_framework import serializers
from .models import Survey, Question, AnswerOption, SurveyResponse, Answer


class AnswerOptionSerializer(serializers.ModelSerializer):
    """Варианты ответов"""

    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'order']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    """Вопросы с вариантами"""
    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'answer_options']
        read_only_fields = ['id']


class SurveySerializer(serializers.ModelSerializer):
    """Список опросов"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'author', 'author_username', 'created_at',
                  'updated_at', 'is_active', 'questions_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author_username', 'questions_count']


class SurveyDetailSerializer(serializers.ModelSerializer):
    """Детали опроса"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'author', 'author_username', 'created_at',
                  'updated_at', 'is_active', 'questions']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author_username']


class AnswerSerializer(serializers.ModelSerializer):
    """Ответы пользователей"""

    class Meta:
        model = Answer
        fields = ['id', 'question', 'answer_option', 'answered_at']
        read_only_fields = ['id', 'answered_at']


class SurveyResponseSerializer(serializers.ModelSerializer):
    """Прохождение опроса"""
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyResponse
        fields = ['id', 'survey', 'user', 'started_at', 'completed_at',
                  'is_completed', 'answers']
        read_only_fields = ['id', 'started_at', 'completed_at', 'is_completed']


class NextQuestionSerializer(serializers.Serializer):
    """Следующий вопрос"""
    question = QuestionSerializer(read_only=True)
    is_last = serializers.BooleanField(read_only=True)
    progress = serializers.DictField(read_only=True)