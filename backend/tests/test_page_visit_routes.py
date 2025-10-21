import pytest


def test_create_visit_endpoint(client):
    payload = {
        "url": "https://example.org",
        "title": "Example Domain",
        "visit_count": 1,
        "last_visit_time": "2023-01-01T12:00:00",
        "typed_count": 0,
        "favicon": "https://example.org/favicon.ico"
    }
    resp = client.post("/visits", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["url"] == payload["url"]


def test_get_visits_by_url_endpoint(client):
    # First create a visit
    payload = {
        "url": "https://example.org",
        "title": "Example Domain",
        "visit_count": 1,
        "last_visit_time": "2023-01-01T12:00:00",
        "typed_count": 0,
        "favicon": "https://example.org/favicon.ico"
    }
    client.post("/visits", json=payload)

    # Then test getting visits by URL
    url = "https://example.org"
    resp = client.get(f"/visits?url={url}")
    assert resp.status_code == 200
    visits = resp.json()
    assert isinstance(visits, list)
    assert len(visits) > 0


def test_get_latest_visit_endpoint(client):
    # First create a visit
    payload = {
        "url": "https://example.org",
        "title": "Example Domain",
        "visit_count": 1,
        "last_visit_time": "2023-01-01T12:00:00",
        "typed_count": 0,
        "favicon": "https://example.org/favicon.ico"
    }
    client.post("/visits", json=payload)

    # Then test getting latest visit
    url = "https://example.org"
    resp = client.get(f"/visits/latest?url={url}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == url


def test_get_stats_endpoint(client):
    # First create some visits
    payloads = [
        {
            "url": "https://example.org",
            "title": "Example Domain",
            "visit_count": 1,
            "last_visit_time": "2023-01-01T12:00:00",
            "typed_count": 0,
            "favicon": "https://example.org/favicon.ico"
        },
        {
            "url": "https://example.com",
            "title": "Example Domain",
            "visit_count": 2,
            "last_visit_time": "2023-01-01T12:00:00",
            "typed_count": 1,
            "favicon": "https://example.com/favicon.ico"
        }
    ]

    for payload in payloads:
        client.post("/visits", json=payload)

    # Then test getting stats
    resp = client.get("/visits/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_visits" in data
    assert "unique_urls" in data


def test_get_recent_visits_endpoint(client):
    # First create some visits
    payloads = [
        {
            "url": "https://example.org",
            "title": "Example Domain",
            "visit_count": 1,
            "last_visit_time": "2023-01-01T12:00:00",
            "typed_count": 0,
            "favicon": "https://example.org/favicon.ico"
        },
        {
            "url": "https://example.com",
            "title": "Example Domain",
            "visit_count": 2,
            "last_visit_time": "2023-01-01T12:00:00",
            "typed_count": 1,
            "favicon": "https://example.com/favicon.ico"
        }
    ]

    for payload in payloads:
        client.post("/visits", json=payload)

    # Then test getting recent visits
    resp = client.get("/visits/recent?limit=3")
    assert resp.status_code == 200
    visits = resp.json()
    assert isinstance(visits, list)
    assert len(visits) <= 3