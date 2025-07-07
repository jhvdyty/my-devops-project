import os
import requests
import redis
import json
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Настройки
SERVICE_API_URL = os.getenv('SERVICE_API_URL', 'http://localhost:5000')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Подключение к Redis
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("\/ Connected to Redis")
except Exception as e:
    print(f"X Redis connection failed: {e}")
    redis_client = None

# Каталог услуг
SERVICES_CATALOG = {
    "services": [
        {
            "id": 1,
            "name": "Name Generator API",
            "description": "Generates random names",
            "version": "1.0.0",
            "endpoint": "/name",
            "status": "active",
            "last_updated": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Health Check API",
            "description": "Basic health check service",
            "version": "1.0.0",
            "endpoint": "/",
            "status": "active",
            "last_updated": "2024-01-01T00:00:00Z"
        }
    ]
}

@app.route("/")
def home():
    return jsonify({
        "service": "Service Catalog",
        "version": "1.0.0",
        "description": "Microservices catalog and discovery service",
        "endpoints": [
            "/services - List all services",
            "/services/{id} - Get service details",
            "/services/health - Check services health",
            "/services/call/{service_id}/{endpoint} - Proxy call to service"
        ]
    })

@app.route("/services", methods=['GET'])
def get_services():
    """Получить список всех сервисов"""
    # Проверяем кеш
    if redis_client:
        cached = redis_client.get('services_catalog')
        if cached:
            return jsonify(json.loads(cached))
    
    # Если кеша нет, возвращаем из памяти и кешируем
    if redis_client:
        redis_client.setex('services_catalog', 300, json.dumps(SERVICES_CATALOG))
    
    return jsonify(SERVICES_CATALOG)

@app.route("/services/<int:service_id>", methods=['GET'])
def get_service(service_id):
    """Получить информацию о конкретном сервисе"""
    service = next((s for s in SERVICES_CATALOG['services'] if s['id'] == service_id), None)
    
    if not service:
        return jsonify({"error": "Service not found"}), 404
    
    return jsonify(service)

@app.route("/services/health", methods=['GET'])
def check_services_health():
    """Проверить здоровье всех сервисов"""
    health_status = {
        "catalog_service": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": []
    }
    
    # Проверяем service-api
    try:
        response = requests.get(f"{SERVICE_API_URL}/", timeout=5)
        if response.status_code == 200:
            health_status["services"].append({
                "name": "service-api",
                "status": "healthy",
                "response_time": response.elapsed.total_seconds(),
                "endpoint": SERVICE_API_URL
            })
        else:
            health_status["services"].append({
                "name": "service-api",
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}",
                "endpoint": SERVICE_API_URL
            })
    except Exception as e:
        health_status["services"].append({
            "name": "service-api",
            "status": "unreachable",
            "error": str(e),
            "endpoint": SERVICE_API_URL
        })
    
    # Проверяем Redis
    if redis_client:
        try:
            redis_client.ping()
            health_status["services"].append({
                "name": "redis",
                "status": "healthy",
                "endpoint": REDIS_URL
            })
        except Exception as e:
            health_status["services"].append({
                "name": "redis",
                "status": "unhealthy",
                "error": str(e),
                "endpoint": REDIS_URL
            })
    else:
        health_status["services"].append({
            "name": "redis",
            "status": "not_configured",
            "endpoint": REDIS_URL
        })
    
    return jsonify(health_status)

@app.route("/services/call/<int:service_id>/<path:endpoint>", methods=['GET', 'POST'])
def proxy_service_call(service_id, endpoint):
    """Проксирование вызовов к другим сервисам"""
    service = next((s for s in SERVICES_CATALOG['services'] if s['id'] == service_id), None)
    
    if not service:
        return jsonify({"error": "Service not found"}), 404
    
    if service['status'] != 'active':
        return jsonify({"error": "Service is not active"}), 503
    
    try:
        # Формируем URL для вызова
        target_url = f"{SERVICE_API_URL}/{endpoint}"
        
        if request.method == 'GET':
            response = requests.get(target_url, 
                                  params=request.args,
                                  timeout=10)
        else:
            response = requests.post(target_url,
                                   json=request.get_json(),
                                   params=request.args,
                                   timeout=10)
        
        # Логируем вызов
        if redis_client:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "service_id": service_id,
                "endpoint": endpoint,
                "method": request.method,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
            redis_client.lpush('service_calls_log', json.dumps(log_entry))
            redis_client.ltrim('service_calls_log', 0, 999)  # Храним только последние 1000 записей
        
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.Timeout:
        return jsonify({"error": "Service timeout"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Service unavailable"}), 503
    except Exception as e:
        return jsonify({"error": f"Proxy error: {str(e)}"}), 500

@app.route("/services/logs", methods=['GET'])
def get_service_logs():
    """Получить логи вызовов сервисов"""
    if not redis_client:
        return jsonify({"error": "Redis not available"}), 503
    
    try:
        logs = redis_client.lrange('service_calls_log', 0, -1)
        parsed_logs = [json.loads(log) for log in logs]
        return jsonify({
            "total_calls": len(parsed_logs),
            "logs": parsed_logs
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get logs: {str(e)}"}), 500

@app.route("/services/stats", methods=['GET'])
def get_service_stats():
    """Получить статистику по сервисам"""
    if not redis_client:
        return jsonify({"error": "Redis not available"}), 503
    
    try:
        logs = redis_client.lrange('service_calls_log', 0, -1)
        stats = {
            "total_calls": len(logs),
            "services": {},
            "endpoints": {},
            "methods": {}
        }
        
        for log_str in logs:
            log = json.loads(log_str)
            service_id = str(log['service_id'])
            endpoint = log['endpoint']
            method = log['method']
            
            # Статистика по сервисам
            if service_id not in stats['services']:
                stats['services'][service_id] = 0
            stats['services'][service_id] += 1
            
            # Статистика по эндпоинтам
            if endpoint not in stats['endpoints']:
                stats['endpoints'][endpoint] = 0
            stats['endpoints'][endpoint] += 1
            
            # Статистика по методам
            if method not in stats['methods']:
                stats['methods'][method] = 0
            stats['methods'][method] += 1
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)