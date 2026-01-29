# Init Project (шаблон FastAPI)

Этот репозиторий — продакшен‑готовый шаблон FastAPI‑backend. Включает:
- модульную структуру API
- auth‑домен и интеграцию с LDAP
- асинхронный SQLAlchemy + Alembic миграции
- конфигурацию через переменные окружения
- единый формат ошибок
- набор unit/integration тестов

Ниже — техническая документация по модулям и эксплуатации.

## Важно для разработки прогнать все hook'и

```
uv run ruff check . --fix
```

```
uv run ruff check . --fix --unsafe-fixes
```

```
uv run black src
```

```
uv run mypy src
```

```
uv run pre-commit run --config ./code_style/.pre-commit-config.yaml
```

### Импорт‑конвенция
Используйте корневые пакеты без `src.`:

```
from api.app import app
from db.models import Base
```


## Структура проекта

```
.
├── alembic/                     # окружение Alembic
│   ├── env.py                    # конфигурация, target_metadata
│   └── versions/                # файлы миграций
├── src/
│   ├── api/                      # FastAPI, роутеры, схемы, зависимости, ошибки
│   ├── auth/                     # auth‑домен, JWT, LDAP, сервис
│   ├── config/                   # настройки и env‑загрузка
│   ├── core/                     # утилиты (логирование)
│   └── db/                       # база, engine, модели, репозитории
├── tests/                        # unit и integration тесты
├── main.py                       # точка входа
├── alembic.ini                   # настройки Alembic
├── pyproject.toml                # зависимости и tooling
└── .env.example                  # пример конфигурации
```

## Требования

- Python 3.13
- PostgreSQL

Зависимости описаны в `pyproject.toml`.

## Установка

Рекомендуемый способ (uv):

```
uv pip install -e .
```

С тестовыми зависимостями:

```
uv pip install -e ".[test]"
```

Если используете обычный venv:

```
python -m pip install -e .
```

## Конфигурация

Настройки читаются из `.env.template` и `.env` с префиксом `APP_CONFIG__`.
Скопируйте `.env.example` в `.env` и заполните значения:

```
cp .env.example .env
```

Ключевые параметры:
- `APP_CONFIG__DB__URL` — async DSN PostgreSQL (sqlalchemy+asyncpg)
- `APP_CONFIG__LDAP__...` — параметры LDAP
- `APP_CONFIG__JWT__...` — параметры JWT
- `APP_CONFIG__LOG__FILE` — путь до лог‑файла

Код конфигурации: `src/config/settings.py`

## Запуск приложения

Точка входа: `main.py`

```
python main.py
```

Либо напрямую через uvicorn:

```
uvicorn api.app:app --reload
```

Роуты доступны под префиксом `settings.api.prefix` (по умолчанию `/api/v1`).

## Модули

### `src/api`
API слой:
- `api/app.py` — фабрика FastAPI, CORS, регистрация роутеров
- `api/routers/v1` — версионированные роутеры
- `api/routers/v1/auth` — login/refresh эндпоинты
- `api/schemas` — pydantic модели
- `api/deps` — зависимости
- `api/errors` — схема ошибок, исключения, обработчики

### `src/auth`
Auth‑домен:
- `auth/domain.py` — dataclass модели
- `auth/jwt_utils.py` — создание/проверка JWT
- `auth/ldap_client.py` — LDAP запросы
- `auth/service.py` — login/refresh оркестрация

### `src/db`
DB слой:
- `db/base.py` — Declarative Base + naming convention
- `db/engine.py` — async engine и контекстные сессии
- `db/models` — ORM модели (например `User`)
- `db/repositories` — доступ к данным (сейчас auth‑репозитории)

### `src/core`
Общие утилиты:
- `core/logging_setup.py` — логирование

## База данных и миграции (Alembic)

Конфиг: `alembic.ini`
Окружение: `alembic/env.py`

Alembic использует `db.models.Base.metadata` для автогенерации.

### Создать миграцию

```
alembic revision --autogenerate -m "Migration message"
```

### Применить миграции

```
alembic upgrade head
```

### Откатить миграцию

```
alembic downgrade -1
```

### Сброс до base

```
alembic downgrade base
```

## Тесты

Запуск:

```
python -m pytest -q
```

Структура тестов:
- API: `tests/test_api_*`
- Auth: `tests/test_auth_*`
- DB: `tests/test_db_*`
- Core/Config: `tests/test_core_*`, `tests/test_config_*`


### Логирование
Инициализируется в `core/logging_setup.py` и вызывается из `main.py`.

### Единая обработка ошибок
`api/errors` регистрирует обработчики для:
- `AppError`
- `RequestValidationError`
- `IntegrityError`
- неотловленных исключений

### Auth‑флоу
Login → LDAP → sync user → выдача access/refresh токенов.
Refresh → проверка refresh‑токена → LDAP → новый access‑токен.

Auth‑эндпоинты:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`


