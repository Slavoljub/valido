from prometheus_client import Gauge, Counter

# Gauges for system resources
CPU_USAGE = Gauge('validoai_cpu_usage_percent', 'CPU Utilisation percentage')
RAM_USAGE = Gauge('validoai_ram_usage_percent', 'RAM Utilisation percentage')
GPU_USAGE = Gauge('validoai_gpu_usage_percent', 'GPU utilisation percentage per device', ['gpu_index'])

# Database up/down gauge (1 up, 0 down)
DB_STATUS = Gauge('validoai_database_status', 'Database availability', ['db'])

# Local model count
LOCAL_MODEL_COUNT = Gauge('validoai_local_models', 'Number of local LLM models detected')

# Counter for API requests (example)
API_REQUESTS = Counter('validoai_api_requests_total', 'Total API requests', ['endpoint'])
