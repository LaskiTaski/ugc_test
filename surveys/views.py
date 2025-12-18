from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, ExpressionWrapper, DurationField, Avg
from django.utils import timezone
from django.db import transaction

from .models import Survey, Question, AnswerOption, SurveyResponse, Answer
from .serializers import SurveySerializer, SurveyDetailSerializer, NextQuestionSerializer


class SurveyViewSet(viewsets.ModelViewSet):
    """API для работы с опросами"""
    queryset = Survey.objects.filter(is_active=True)
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurveyDetailSerializer
        return SurveySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'])
    def next_question(self, request, pk=None):
        """Получить следующий вопрос для прохождения"""
        survey = self.get_object()
        user = request.user

        survey_response, created = SurveyResponse.objects.get_or_create(
            survey=survey,
            user=user,
            defaults={'is_completed': False}
        )

        if survey_response.is_completed:
            return Response({
                'message': 'Вы уже завершили этот опрос',
                'completed_at': survey_response.completed_at
            })

        all_questions = survey.questions.all().order_by('order')
        total_questions = all_questions.count()

        if total_questions == 0:
            return Response(
                {'message': 'В опросе нет вопросов'},
                status=status.HTTP_404_NOT_FOUND
            )

        answered_question_ids = survey_response.answers.values_list('question_id', flat=True)
        answered_count = len(answered_question_ids)
        next_question = all_questions.exclude(id__in=answered_question_ids).first()

        if next_question is None:
            survey_response.is_completed = True
            survey_response.completed_at = timezone.now()
            survey_response.save()

            return Response({
                'message': 'Опрос завершен! Спасибо за участие.',
                'completed_at': survey_response.completed_at,
                'total_questions': total_questions
            })

        serializer = NextQuestionSerializer({
            'question': next_question,
            'is_last': (answered_count + 1 == total_questions),
            'progress': {
                'current': answered_count + 1,
                'total': total_questions,
                'percentage': round((answered_count / total_questions) * 100, 2)
            }
        })

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Отправить ответ на вопрос"""
        survey = self.get_object()
        user = request.user

        question_id = request.data.get('question_id')
        answer_option_id = request.data.get('answer_option_id')

        if not question_id or not answer_option_id:
            return Response(
                {'error': 'Необходимо указать question_id и answer_option_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        question = get_object_or_404(Question, id=question_id, survey=survey)
        answer_option = get_object_or_404(AnswerOption, id=answer_option_id, question=question)

        survey_response, _ = SurveyResponse.objects.get_or_create(
            survey=survey,
            user=user
        )

        if survey_response.is_completed:
            return Response(
                {'error': 'Опрос уже завершен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            answer, created = Answer.objects.update_or_create(
                survey_response=survey_response,
                question=question,
                defaults={'answer_option': answer_option}
            )

        return Response({
            'message': f'Ответ {"создан" if created else "обновлен"}',
            'answer_id': answer.id
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Статистика по опросу"""
        survey = self.get_object()

        if survey.author != request.user:
            return Response(
                {'error': 'Только автор опроса может просматривать статистику'},
                status=status.HTTP_403_FORBIDDEN
            )

        total_responses = SurveyResponse.objects.filter(survey=survey).count()
        completed_responses = SurveyResponse.objects.filter(survey=survey, is_completed=True).count()

        avg_completion_time = None
        completed_survey_responses = SurveyResponse.objects.filter(
            survey=survey,
            is_completed=True,
            completed_at__isnull=False
        )

        if completed_survey_responses.exists():
            time_deltas = completed_survey_responses.annotate(
                duration=ExpressionWrapper(
                    F('completed_at') - F('started_at'),
                    output_field=DurationField()
                )
            ).aggregate(avg_duration=Avg('duration'))

            if time_deltas['avg_duration']:
                avg_completion_time = time_deltas['avg_duration'].total_seconds()

        questions_stats = []
        for question in survey.questions.all().order_by('order'):
            answer_counts = Answer.objects.filter(question=question).values(
                'answer_option__id', 'answer_option__text'
            ).annotate(count=Count('id')).order_by('-count')

            total_answers = sum(item['count'] for item in answer_counts)

            options_stats = [
                {
                    'option_id': item['answer_option__id'],
                    'option_text': item['answer_option__text'],
                    'count': item['count'],
                    'percentage': round((item['count'] / total_answers * 100), 2) if total_answers > 0 else 0
                }
                for item in answer_counts
            ]

            questions_stats.append({
                'question_id': question.id,
                'question_text': question.text,
                'order': question.order,
                'total_answers': total_answers,
                'options': options_stats
            })

        return Response({
            'survey_id': survey.id,
            'survey_title': survey.title,
            'total_responses': total_responses,
            'completed_responses': completed_responses,
            'completion_rate': round((completed_responses / total_responses * 100), 2) if total_responses > 0 else 0,
            'avg_completion_time_seconds': avg_completion_time,
            'questions_statistics': questions_stats
        })