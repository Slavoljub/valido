from __future__ import annotations

import time
from typing import Dict, Any

from src.monitoring import system_monitor

_CACHE_TTL = 1.0  # seconds
_last_ts = 0.0
_last_payload: Dict[str, Any] | None = None


def get_metrics() -> Dict[str, Any]:
    global _last_ts, _last_payload
    now = time.time()
    if _last_payload is None or now - _last_ts > _CACHE_TTL:
        _last_payload = system_monitor.collect()
        _last_ts = now
    return _last_payload
