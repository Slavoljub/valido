import sqlite3
from typing import Dict, Any

DB_PATH = 'data/sqlite/app.db'

def get_realtime_metrics() -> Dict[str, Any]:
    """Return simple metrics from sqlite (example_pages count) or error message."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM example_pages")
        (count,) = cur.fetchone()
        conn.close()
        return {
            'status': 'online',
            'example_pages': count
        }
    except Exception as e:
        return {
            'status': 'server_down',
            'error': str(e)
        }
