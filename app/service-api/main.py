import random
import os
import psutil 
import time
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# Глобальные счетчики для метрик
metrics_counters = {
    'requests_total': {
        'GET_/': 0,
        'GET_/name': 0,
        'GET_/health': 0,
        'GET_/status': 0,
        'GET_/info': 0,
        'GET_/metrics': 0
    },
    'response_time_total': 0,
    'response_count': 0
}

start_time = time.time()

def increment_counter(method, endpoint):
    """Увеличить счетчик запросов"""
    key = f"{method}_{endpoint}"
    if key in metrics_counters['requests_total']:
        metrics_counters['requests_total'][key] += 1

@app.route("/")
def hello():
    increment_counter('GET', '/')
    return jsonify({
        "service": "Service API",
        "version": "1.0.0",
        "description": "Microservice for generating random names",
        "endpoints": [
            "/ - Service information",
            "/name - Generate random name",
            "/health - Health check",
            "/metrics - Prometheus metrics"
        ]
    })

@app.route("/name")
def random_name():
    """Генерация случайного имени"""
    increment_counter('GET', '/name')
    
    vowels = ['a', 'e', 'y', 'u', 'o', 'i']
    consonants = ['w', 'r', 't', 'p', 's', 'd', 'f', 'g', 'h', 'm', 'v', 'k', 'n', 'b', 'l', 'c']
    
    name_length = random.randint(3, 8)
    name = ''
    use_vowel = random.choice([True, False])
    
    for i in range(name_length):
        if use_vowel:
            name += random.choice(vowels)
        else:
            name += random.choice(consonants)
        
        if random.random() > 0.7: 
            use_vowel = not use_vowel
        else:
            use_vowel = not use_vowel
    
    formatted_name = name[0].upper() + name[1:]
    
    return jsonify({
        "name": formatted_name,
        "length": len(formatted_name),
        "generated_at": datetime.now().isoformat()
    })

@app.route("/health")
def health_check():
    """Проверка здоровья сервиса"""
    increment_counter('GET', '/health')
    return jsonify({
        "status": "healthy",
        "service": "service-api",
        "version": "1.0.0",
        "uptime": f"{time.time() - start_time:.2f}s"
    })

@app.route("/names/<int:count>")
def generate_multiple_names(count):
    """Генерация нескольких имен"""
    increment_counter('GET', '/names')
    
    if count > 100:
        return jsonify({"error": "Maximum 100 names allowed"}), 400
    
    if count < 1:
        return jsonify({"error": "Count must be at least 1"}), 400
    
    names = []
    for _ in range(count):
        vowels = ['a', 'e', 'y', 'u', 'o', 'i']
        consonants = ['w', 'r', 't', 'p', 's', 'd', 'f', 'g', 'h', 'm', 'v', 'k', 'n', 'b', 'l', 'c']
        
        name_length = random.randint(3, 8)
        name = ''
        use_vowel = random.choice([True, False])
        
        for i in range(name_length):
            if use_vowel:
                name += random.choice(vowels)
            else:
                name += random.choice(consonants)
            
            if random.random() > 0.7:
                use_vowel = not use_vowel
            else:
                use_vowel = not use_vowel
        
        formatted_name = name[0].upper() + name[1:]
        names.append(formatted_name)
    
    return jsonify({
        "names": names,
        "count": len(names),
        "generated_at": datetime.now().isoformat()
    })

@app.route("/metrics")
def metrics():
    """Метрики для Prometheus в правильном формате"""
    increment_counter('GET', '/metrics')
    
    # Получаем текущее время для uptime
    uptime_seconds = time.time() - start_time
    
    # Получаем использование памяти
    try:
        memory_usage = psutil.virtual_memory().used
        memory_percent = psutil.virtual_memory().percent
    except:
        memory_usage = 0
        memory_percent = 0
    
    # Формируем метрики в формате Prometheus
    metrics_output = f"""# HELP service_api_requests_total Total number of HTTP requests
# TYPE service_api_requests_total counter
service_api_requests_total{{method="GET",endpoint="/"}} {metrics_counters['requests_total']['GET_/']}
service_api_requests_total{{method="GET",endpoint="/name"}} {metrics_counters['requests_total']['GET_/name']}
service_api_requests_total{{method="GET",endpoint="/health"}} {metrics_counters['requests_total']['GET_/health']}
service_api_requests_total{{method="GET",endpoint="/status"}} {metrics_counters['requests_total']['GET_/status']}
service_api_requests_total{{method="GET",endpoint="/info"}} {metrics_counters['requests_total']['GET_/info']}
service_api_requests_total{{method="GET",endpoint="/metrics"}} {metrics_counters['requests_total']['GET_/metrics']}

# HELP service_api_up Service availability (1 = up, 0 = down)
# TYPE service_api_up gauge
service_api_up 1

# HELP service_api_uptime_seconds Service uptime in seconds
# TYPE service_api_uptime_seconds gauge
service_api_uptime_seconds {uptime_seconds:.2f}

# HELP service_api_memory_usage_bytes Current memory usage in bytes
# TYPE service_api_memory_usage_bytes gauge
service_api_memory_usage_bytes {memory_usage}

# HELP service_api_memory_usage_percent Current memory usage percentage
# TYPE service_api_memory_usage_percent gauge
service_api_memory_usage_percent {memory_percent}

# HELP service_api_version_info Version information
# TYPE service_api_version_info gauge
service_api_version_info{{version="1.0.0",service="service-api"}} 1

# HELP service_api_start_time_seconds Unix timestamp when the service started
# TYPE service_api_start_time_seconds gauge
service_api_start_time_seconds {start_time}
"""
    
    # Возвращаем метрики как plain text
    from flask import Response
    return Response(metrics_output, mimetype='text/plain')

@app.route("/status")
def status():
    """Детальный статус сервиса"""
    increment_counter('GET', '/status')
    return jsonify({
        "service": "service-api",
        "status": "running",
        "uptime": f"{time.time() - start_time:.2f}s",
        "version": "1.0.0",
        "environment": os.getenv("FLASK_ENV", "production"),
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/": "Service information",
            "/name": "Generate random name",
            "/names/<count>": "Generate multiple names",
            "/health": "Health check",
            "/metrics": "Prometheus metrics",
            "/status": "Detailed status"
        },
        "metrics": {
            "requests_total": sum(metrics_counters['requests_total'].values()),
            "uptime_seconds": time.time() - start_time
        }
    })

@app.route("/info")
def info():
    """Информация о системе"""
    increment_counter('GET', '/info')
    return jsonify({
        "service": "service-api",
        "version": "1.0.0",
        "python_version": "3.x",
        "environment": os.getenv("FLASK_ENV", "production"),
        "dependencies": {
            "flask": "available",
            "random": "available",
            "psutil": "available" if 'psutil' in globals() else "not available"
        },
        "uptime": f"{time.time() - start_time:.2f}s"
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    print(f"Starting service-api on port {port}")
    print(f"Metrics will be available at http://localhost:{port}/metrics")
    app.run(host="0.0.0.0", port=port, debug=debug)