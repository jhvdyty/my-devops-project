# Документация проекта

## Архитектура
- Микросервисы: service-api, service-catalog
- Инфраструктура через Terraform, Kubernetes, Ansible

## Запуск
```bash
docker build -t service-api ./app/service-api
docker run -p 8080:80 service-api
