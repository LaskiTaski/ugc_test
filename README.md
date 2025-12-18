# UGC Survey System

Система для создания и прохождения пользовательских опросов.

## Описание

Приложение позволяет:
- Создавать опросы с упорядоченными вопросами и вариантами ответов
- Проходить опросы с отслеживанием прогресса
- Просматривать статистику по опросам (для авторов)

## Модели данных

**Survey** - опрос (название, автор, даты)

**Question** - вопрос с порядком отображения

**AnswerOption** - варианты ответов с порядком

**SurveyResponse** - прохождение опроса пользователем

**Answer** - ответ на конкретный вопрос

### Ключевые особенности

- Индексы БД на часто запрашиваемых полях
- Уникальные ограничения для предотвращения дубликатов
- Connection pooling для эффективной работы с БД

## Запуск

### С Docker
```bash
docker-compose up -d --build
docker-compose exec web python manage.py createsuperuser
```

Приложение доступно на http://localhost:8000

### Без Docker
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate для Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API

**Список опросов:** `GET /api/surveys/`

**Следующий вопрос:** `GET /api/surveys/{id}/next_question/`

**Отправить ответ:** `POST /api/surveys/{id}/submit_answer/`
```json
{
  "question_id": 1,
  "answer_option_id": 1
}
```

**Статистика:** `GET /api/surveys/{id}/statistics/`

**Admin панель:** http://localhost:8000/admin/

## Пример ответа next_question
```json
{
  "question": {
    "id": 1,
    "text": "Ты любишь буратту с помидорами?",
    "order": 1,
    "answer_options": [
      {"id": 1, "text": "Да", "order": 1},
      {"id": 2, "text": "Нет", "order": 2}
    ]
  },
  "is_last": false,
  "progress": {
    "current": 1,
    "total": 4,
    "percentage": 0.0
  }
}
```
