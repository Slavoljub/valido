from __future__ import annotations

import time
from typing import Callable

from prometheus_client import Gauge, Counter

from src.services import realtime_service
from src.monitoring.prometheus_exporter import (
    CPU_USAGE, RAM_USAGE, GPU_USAGE, DB_STATUS, LOCAL_MODEL_COUNT
)


def update_prometheus_metrics(payload: dict[str, object] | None = None) -> None:
    """Push latest data to Prometheus gauges. If payload provided use it, else call service."""
    if payload is None:
        payload = realtime_service.get_metrics()

    sys = payload.get('system', {})  # type: ignore
    CPU_USAGE.set(sys.get('cpu', 0))  # type: ignore
    RAM_USAGE.set(sys.get('ram', 0))  # type: ignore

    gpu_list = sys.get('gpu', []) if isinstance(sys.get('gpu', []), list) else []  # type: ignore
    for idx, util in enumerate(gpu_list):
        GPU_USAGE.labels(gpu_index=str(idx)).set(util)

    dbs = payload.get('databases', {})  # type: ignore
    for name, meta in dbs.items():  # type: ignore
        status = 1 if meta.get('status') == 'online' else 0  # type: ignore
        DB_STATUS.labels(db=name).set(status)

    lm = payload.get('local_models', {})  # type: ignore
    LOCAL_MODEL_COUNT.set(lm.get('count', 0))  # type: ignore


def start_updater(loop_func: Callable[[], None]) -> None:
    """Blocking loop that calls loop_func every 2 seconds"""
    while True:
        loop_func()
        time.sleep(2)
