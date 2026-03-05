import prometheus_client

def test_metrics_endpoint(test_app, test_client):
    """Ensure /metrics endpoint is exposed and returns Prometheus format."""
    with test_app.app_context():
        resp = test_client.get('/metrics')
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        # Should include at least one of our custom gauges
        assert 'validoai_cpu_usage_percent' in text
        assert resp.headers['Content-Type'].startswith('text/plain')


def test_gauge_update():
    """Verify that update_prometheus_metrics pushes values into the registry."""
    from src.monitoring.metrics_updater import update_prometheus_metrics
    from src.monitoring.prometheus_exporter import CPU_USAGE

    update_prometheus_metrics()

    # Fetch metric value from default registry
    metric_samples = [s for s in CPU_USAGE.collect()][0].samples
    # At least one sample exists with a float value (>=0)
    assert metric_samples
    assert metric_samples[0].value >= 0
