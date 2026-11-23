from core import Event, IncidentStore


def test_isolated_low_risk_event():
    store = IncidentStore()
    incident = store.ingest(Event(source="wazuh", kind="process_exec", host="lab-01", timestamp="2026-08-20T00:00:00Z", confidence=0.8))
    assert 0 <= incident.score < 30


def test_correlated_execution_and_network_is_higher_risk():
    store = IncidentStore()
    store.ingest(Event(source="tetragon", kind="process_exec", host="lab-02", timestamp="2026-08-20T00:00:00Z", process="demo", confidence=0.95))
    incident = store.ingest(Event(source="tetragon", kind="network_connect", host="lab-02", timestamp="2026-08-20T00:00:01Z", process="demo", remote_ip="192.0.2.10", confidence=0.95))
    assert incident.score >= 20
    assert any("process-to-network" in reason for reason in incident.reasons)


def test_yara_plus_execution_correlation():
    store = IncidentStore()
    store.ingest(Event(source="tetragon", kind="process_exec", host="lab-03", timestamp="2026-08-20T00:00:00Z", process="demo", confidence=1.0))
    incident = store.ingest(Event(source="yara", kind="yara_match", host="lab-03", timestamp="2026-08-20T00:00:01Z", file_path="/tmp/sample", confidence=1.0))
    assert incident.score >= 60
    assert any("malware-indicator" in reason for reason in incident.reasons)
