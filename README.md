# Gromov A.S. Test Task - Ticket System

REST API сервис для управления обращениями клиентов (тикет-система).

## Description

Сервис реализует систему обработки обращений клиентов.

Основные возможности:
- управление клиентами и операторами
- создание и обработка тикетов
- обмен сообщениями в рамках тикета
- автоматическое назначение тикетов операторам
- кэширование статистики в Redis
- автоматическое закрытие тикетов в статусе waiting

Сервис реализован в рамках тестового задания.

## Tech Stack

- Python 3.11
- aiohttp
- SQLAlchemy 2.x (async)
- PostgreSQL
- Redis
- Alembic
- Docker Compose

## Run project

### 1. Клонировать репозиторий

git clone <repo>
cd project

### 2. Создание окружения

docker compose up -d

### 3. Установить зависимости

pip install -r requirements.txt

### 4. Применить миграции

alembic upgrade head

### 5. Запуск основного приложения

python main.py