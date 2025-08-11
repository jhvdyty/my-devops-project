# Microservices Platform

Микросервисная платформа с автоматическим обнаружением сервисов, мониторингом, кешированием и балансировкой нагрузки.

##  Архитектура системы

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Nginx    │◄──►│ Service Catalog │◄──►│   Service API   │
│  (Gateway)  │    │  (Discovery)    │    │ (Name Generator)│
└─────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
      │                      │                      │
      ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Shared Infrastructure                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │    Redis    │  │ Prometheus  │        │
│  │ (Database)  │  │  (Cache)    │  │(Monitoring) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │     Grafana     │
                    │  (Dashboards)   │
                    └─────────────────┘
```

##  Технологический стек

### Backend Services
- **Python Flask** - Микросервисы
- **PostgreSQL 16** - Основная база данных
- **Redis 7** - Кеширование и сессии
- **Nginx** - Reverse proxy и load balancer

### Мониторинг и DevOps
- **Prometheus** - Сбор метрик
- **Grafana** - Визуализация данных
- **Docker** - Контейнеризация
- **Terraform** - Infrastructure as Code
- **GitHub Actions** - CI/CD пайплайны

##  Быстрый старт

### Предварительные требования
- Docker и Docker Compose
- Git
- 4GB RAM и 20GB свободного места

### Установка и запуск

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd microservices-platform
```

2. **Запустите все сервисы:**
```bash
docker-compose up -d
```

3. **Проверьте статус сервисов:**
```bash
docker-compose ps
```

### Доступ к сервисам

| Сервис | URL | Порт | Описание |
|--------|-----|------|----------|
|  **API Gateway** | http://localhost | 80 | Главная точка входа |
|  **Service API** | http://localhost:5000 | 5000 | Генератор имен |
|  **Service Catalog** | http://localhost:5001 | 5001 | Реестр сервисов |
|  **Prometheus** | http://localhost:9090 | 9090 | Метрики и мониторинг |
|  **Grafana** | http://localhost:3000 | 3000 | Дашборды (admin/admin) |
|  **PostgreSQL** | localhost:5432 | 5432 | База данных |
|  **Redis** | localhost:6379 | 6379 | Кеш и сессии |

##  Структура проекта

```
.
├── app/                           # Микросервисы
│   ├── service-api/              # API генерации имен
│   │   ├── main.py               # Основной код сервиса
│   │   ├── requirements.txt      # Зависимости Python
│   │   └── Dockerfile           # Образ контейнера
│   └── service-catalog/          # Каталог сервисов
│       ├── main.py               # Реестр и discovery
│       ├── requirements.txt      # Зависимости Python
│       └── Dockerfile           # Образ контейнера
├── database/                     # База данных
│   └── init.sql                 # Инициализация схемы
├── monitoring/                   # Мониторинг
│   ├── prometheus.yml           # Конфигурация Prometheus
│   └── alerts.yml               # Правила алертов
├── nginx/                        # Reverse proxy
│   └── nginx.conf               # Конфигурация Nginx
├── infrastructure/terraform/     # Infrastructure as Code
│   └── main.tf                  # Terraform конфигурация
├── .github/workflows/           # CI/CD пайплайны
├── docs/                        # Документация
│   └── README.md               # Техническая документация
└── docker-compose.yml           # Описание сервисов
```

##  Сервисы

### 1. Service API (Генератор имен)
**Порт:** 5000  
**Эндпоинты:**
- `GET /` - Информация о сервисе
- `GET /name` - Генерация случайного имени
- `GET /names/<count>` - Генерация множественных имен (до 100)
- `GET /health` - Проверка здоровья
- `GET /status` - Детальный статус
- `GET /metrics` - Метрики Prometheus

**Пример использования:**
```bash
# Генерация одного имени
curl http://localhost:5000/name

# Генерация 5 имен
curl http://localhost:5000/names/5

# Проверка здоровья
curl http://localhost:5000/health
```

### 2. Service Catalog (Реестр сервисов)
**Порт:** 5001  
**Эндпоинты:**
- `GET /services` - Список всех сервисов
- `GET /services/<id>` - Информация о сервисе
- `GET /services/health` - Здоровье всех сервисов
- `GET /services/call/<service_id>/<endpoint>` - Проксирование вызовов
- `GET /services/discover` - Автообнаружение сервисов
- `GET /services/logs` - Логи вызовов
- `GET /services/stats` - Статистика использования

**Пример использования:**
```bash
# Список сервисов
curl http://localhost:5001/services

# Вызов через прокси (service-api через catalog)
curl http://localhost:5001/services/call/1/name

# Проверка здоровья всех сервисов
curl http://localhost:5001/services/health
```

##  API Gateway (Nginx)

Nginx настроен как reverse proxy и балансировщик нагрузки:

- **Основные маршруты:** `/` → Service Catalog
- **API маршруты:** `/api/` → Service API
- **Мониторинг:** `/metrics` → Prometheus метрики
- **Статические файлы:** Кеширование и оптимизация

##  Мониторинг и метрики

### Prometheus метрики

**Service API:**
- `service_api_requests_total` - Общее количество запросов
- `service_api_uptime_seconds` - Время работы сервиса
- `service_api_memory_usage_bytes` - Использование памяти
- `service_api_up` - Доступность сервиса

**Service Catalog:**
- `service_catalog_requests_total` - Запросы к каталогу
- `service_catalog_proxy_calls_total` - Проксированные вызовы
- `service_catalog_services_count` - Количество сервисов
- `service_catalog_redis_connected` - Статус Redis

### Grafana дашборды
- **Service Overview** - Общая статистика сервисов
- **API Performance** - Производительность API
- **Infrastructure** - Состояние инфраструктуры
- **Business Metrics** - Бизнес-метрики

##  База данных

### PostgreSQL
- **База:** `microservices_db`
- **Пользователь:** `postgres`
- **Пароль:** `password`
- **Порт:** `5432`

### Redis
- **Использование:** Кеширование, логирование вызовов
- **Порт:** `6379`
- **Конфигурация:** Базовая настройка без персистентности

##  Конфигурация

### Переменные окружения

```env
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/microservices_db

# Redis
REDIS_URL=redis://redis:6379/0

# Services
SERVICE_API_URL=http://service-api:5000

# Flask
FLASK_ENV=development
PORT=5000
```

### Development режим

```bash
# Запуск в режиме разработки с hot-reload
docker-compose up --build

# Просмотр логов
docker-compose logs -f service-api
docker-compose logs -f service-catalog
```

##  Тестирование

### Локальное тестирование API

```bash
# Тестирование Service API
curl -X GET http://localhost:5000/name
curl -X GET http://localhost:5000/health
curl -X GET http://localhost:5000/metrics

# Тестирование Service Catalog
curl -X GET http://localhost:5001/services
curl -X GET http://localhost:5001/services/health
curl -X GET http://localhost:5001/services/call/1/name
```

### Health Checks

```bash
# Проверка всех сервисов
docker-compose exec service-catalog curl http://localhost:5000/services/health

# Индивидуальные проверки
curl http://localhost:5000/health  # Service API
curl http://localhost:5001/health  # Service Catalog
```

##  Деплой

### Local Development
```bash
docker-compose up -d
```

### Staging/Production
```bash
# Используйте production конфигурацию
docker-compose -f docker-compose.prod.yml up -d

# Или с Terraform
cd infrastructure/terraform
terraform init
terraform apply
```

### CI/CD Pipeline
GitHub Actions автоматически:
1. Запускает тесты
2. Собирает Docker образы
3. Проводит деплой в staging
4. Выполняет smoke tests

##  Безопасность

### Рекомендации:
- Смените пароли по умолчанию в production
- Используйте HTTPS для внешнего доступа
- Настройте файрвол и VPN для внутренней сети
- Регулярно обновляйте зависимости
- Мониторьте подозрительную активность

### Секреты управления:
```bash
# Используйте Docker secrets в production
docker secret create db_password password.txt
docker secret create redis_password redis_pass.txt
```

##  Масштабирование

### Горизонтальное масштабирование:
```bash
# Увеличение количества реплик сервисов
docker-compose up --scale service-api=3 --scale service-catalog=2
```

### Производительность:
- Nginx load balancing между репликами
- Redis для кеширования частых запросов
- Connection pooling для PostgreSQL
- Асинхронная обработка длительных операций

##  Отладка

### Типичные проблемы:

**Сервисы не стартуют:**
```bash
# Проверка логов
docker-compose logs service-api
docker-compose logs service-catalog

# Проверка сети
docker network ls
docker network inspect microservices_default
```

**База данных недоступна:**
```bash
# Проверка PostgreSQL
docker-compose exec postgres psql -U postgres -d microservices_db

# Проверка Redis
docker-compose exec redis redis-cli ping
```

**Проблемы с производительностью:**
```bash
# Мониторинг ресурсов
docker stats
docker-compose top
```

##  Документация

- **API документация:** `/docs/README.md`
- **Swagger UI:** Планируется в следующих версиях
- **Архитектурные решения:** `/docs/architecture.md`
- **Deployment Guide:** `/docs/deployment.md`

##  Участие в разработке

1. Форкните репозиторий
2. Создайте feature ветку
3. Добавьте тесты для новой функциональности
4. Убедитесь, что все тесты проходят
5. Создайте Pull Request

### Code Style:
- Используйте Black для форматирования Python
- Следуйте PEP 8
- Добавляйте docstrings для всех функций
- Покрывайте код тестами

##  Лицензия

Проект распространяется под лицензией MIT. См. файл `LICENSE`.

##  Поддержка

- **Issues:** GitHub Issues для багов и feature requests
- **Документация:** Проверьте `/docs/` для детальной информации
- **Мониторинг:** Используйте Grafana дашборды для диагностики
- **Логи:** `docker-compose logs -f <service-name>`

---

**Готово к использованию!** Запустите `docker-compose up -d` и начните работать с микросервисной платформой.