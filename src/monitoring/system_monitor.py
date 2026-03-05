from __future__ import annotations

"""Centralised system/resource and DB health collector.
Returns plain dict so all transports (REST, WebSocket, gRPC) can reuse it.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from pathlib import Path

import psutil

# ---------------------------------------------------------------------------
# Optional GPU support ------------------------------------------------------
# ---------------------------------------------------------------------------

gpu_supported = False
try:
    import pynvml  # type: ignore

    pynvml.nvmlInit()
    gpu_supported = True
except Exception:  # pragma: no cover – GPU absent
    gpu_supported = False

# ---------------------------------------------------------------------------
# Database health helpers ---------------------------------------------------
# ---------------------------------------------------------------------------


def _check_sqlite() -> Dict[str, Any]:
    from pathlib import Path

    db_path = Path('data/sqlite/app.db')
    return {'status': 'online' if db_path.exists() else 'missing'}


def _check_postgres() -> Dict[str, Any]:
    try:
        from src.database import connection_manager  # lazy import
        connection_manager.test_connection('postgresql')  # type: ignore
        return {'status': 'online'}
    except Exception as e:
        return {'status': 'offline', 'error': str(e)}


def _check_mysql() -> Dict[str, Any]:
    try:
        from src.database import connection_manager  # type: ignore
        connection_manager.test_connection('mysql')  # type: ignore
        return {'status': 'online'}
    except Exception as e:
        return {'status': 'offline', 'error': str(e)}


def _check_local_models() -> Dict[str, Any]:
    """Return list of local LLM model gguf/other files in local_llm_models directory."""
    base = Path('local_llm_models')
    if not base.exists():
        return {'status': 'missing_dir'}

    models = []
    for p in base.rglob('*.gguf'):
        models.append({
            'name': p.stem,
            'size_mb': round(p.stat().st_size / (1024**2), 1),
            'relative_path': str(p.relative_to(base))
        })

    return {
        'status': 'online' if models else 'no_models',
        'count': len(models),
        'models': models[:10]  # limit to avoid huge payload
    }


# ---------------------------------------------------------------------------
# Main collector ------------------------------------------------------------
# ---------------------------------------------------------------------------


def collect() -> Dict[str, Any]:
    """Collect current metrics (CPU, RAM, GPU, DB health)."""
    cpu_percent = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()

    gpu_list: List[int] = []
    if gpu_supported:
        try:
            device_count = pynvml.nvmlDeviceGetCount()  # type: ignore
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)  # type: ignore
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)  # type: ignore
                gpu_list.append(util.gpu)
        except Exception:  # pragma: no cover
            gpu_list = []

    data: Dict[str, Any] = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'system': {
            'cpu': cpu_percent,
            'ram': ram.percent,
            'gpu': gpu_list,
        },
        'databases': {
            'sqlite': _check_sqlite(),
            'postgres': _check_postgres(),
            'mysql': _check_mysql(),
        }
    }
    data['local_models'] = _check_local_models()
    return data


if __name__ == '__main__':  # manual debug
    import json, time
    while True:
        print(json.dumps(collect(), indent=2))
        time.sleep(2)
