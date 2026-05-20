```
project/
├── main.py                    # Главный файл FastAPI
├── database.py                # Подключение к БД
├── core/
│   ├── __init__.py
│   ├── config.py              # Настройки
│   └── models/
│       ├── __init__.py
│       ├── base.py            # Абстрактные модели
│       ├── user.py            # Модель пользователя
│       ├── post.py            # Модель поста
│       └── comment.py         # Модель комментария
├── api/
│   ├── __init__.py
│   ├── dependencies.py        # Зависимости (get_db, get_current_user)
│   └── v1/
│       ├── __init__.py
│       ├── router.py          # Главный роутер v1
│       ├── posts.py           # Роуты для постов
│       ├── comments.py        # Роуты для комментариев
│       ├── users.py           # Роуты для пользователей
│       └── auth.py            # Роуты для аутентификации
├── schemas/
│   ├── __init__.py
│   ├── base.py                # Базовые схемы
│   ├── post.py                # Схемы для постов
│   ├── comment.py             # Схемы для комментариев
│   └── user.py                # Схемы для пользователей
├── services/
│   ├── __init__.py
│   ├── post_service.py        # Бизнес-логика для постов
│   ├── comment_service.py     # Бизнес-логика для комментариев
│   └── user_service.py        # Бизнес-логика для пользователей
└── utils/
    ├── __init__.py
    └── file_service.py        # Сервис для работы с файлами
```
