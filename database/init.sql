-- Инициализация базы данных для микро сервисов
-- Этот файл автоматически выполняется при создании контейнера PostgreSQL

-- Создание схемы для каталога сервисов
CREATE SCHEMA IF NOT EXISTS catalog;

-- Таблица для регистрации сервисов
CREATE TABLE IF NOT EXISTS catalog.services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50),
    endpoint VARCHAR(255),
    host VARCHAR(255),
    port INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    health_check_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для логов вызовов сервисов
CREATE TABLE IF NOT EXISTS catalog.service_calls (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES catalog.services(id),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для мониторинга здоровья сервисов
CREATE TABLE IF NOT EXISTS catalog.health_checks (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES catalog.services(id),
    status VARCHAR(50),
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставка начальных данных
INSERT INTO catalog.services (name, description, version, endpoint, host, port, health_check_url) 
VALUES 
    ('Service API', 'Основной API сервис для генерации имен', '1.0.0', '/', 'service-api', 5000, '/'),
    ('Service Catalog', 'Каталог и мониторинг сервисов', '1.0.0', '/', 'service-catalog', 5000, '/services/health')
ON CONFLICT DO NOTHING;

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_services_status ON catalog.services(status);
CREATE INDEX IF NOT EXISTS idx_service_calls_service_id ON catalog.service_calls(service_id);
CREATE INDEX IF NOT EXISTS idx_service_calls_created_at ON catalog.service_calls(created_at);
CREATE INDEX IF NOT EXISTS idx_health_checks_service_id ON catalog.health_checks(service_id);
CREATE INDEX IF NOT EXISTS idx_health_checks_checked_at ON catalog.health_checks(checked_at);

-- Создание функции для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создание триггера для автоматического обновления updated_at
CREATE TRIGGER update_services_updated_at 
    BEFORE UPDATE ON catalog.services 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Создание пользователя для приложения (опционально)
-- CREATE USER app_user WITH PASSWORD 'app_password';
-- GRANT USAGE ON SCHEMA catalog TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA catalog TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA catalog TO app_user;

-- Вывод информации о созданных объектах
SELECT 'Database initialized successfully' AS status;
SELECT 'Services table created with ' || COUNT(*) || ' records' AS services_info 
FROM catalog.services;