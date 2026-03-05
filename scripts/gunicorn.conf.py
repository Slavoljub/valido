# Gunicorn configuration for ValidoAI
# Usage: gunicorn -c gunicorn.conf.py app:create_app('production')

import os
import multiprocessing

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'validoai'

# Server mechanics
daemon = False
pidfile = os.getenv('GUNICORN_PIDFILE', '/tmp/gunicorn.pid')
user = os.getenv('GUNICORN_USER')
group = os.getenv('GUNICORN_GROUP')
tmp_upload_dir = None

# SSL (if needed)
keyfile = os.getenv('GUNICORN_KEYFILE')
certfile = os.getenv('GUNICORN_CERTFILE')

# Performance tuning
preload_app = True
worker_tmp_dir = '/dev/shm'
