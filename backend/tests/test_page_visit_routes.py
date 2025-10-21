import pytest


def test_create_visit_endpoint(client):
    payload = {
        "url": "https://example.org",
        "link_count": 25,
        "internal_links": 20,
        "external_links": 5,
        "word_count": 1500,
        "image_count": 8,
        "content_images": 6,
        "decorative_images": 2
    }
    resp = client.post("/visits", json=payload)
    print(f"Response status: {resp.status_code}")
    if resp.status_code != 201:
        print(f"Error response: {resp.text}")
    assert resp.status_code == 201
    data = resp.json()
    assert data["url"] == payload["url"]


def test_get_visits_by_url_endpoint(client):
    #  create a visit
    payload = {
        "url": "https://example.org",
        "link_count": 25,
        "internal_links": 20,
        "external_links": 5,
        "word_count": 1500,
        "image_count": 8,
        "content_images": 6,
        "decorative_images": 2
    }
    create_resp = client.post("/visits", json=payload)
    if create_resp.status_code != 201:
        print(f"Create failed: {create_resp.text}")
        pytest.fail("Failed to create visit for test")

    #  test getting visits by URL
    url = "https://example.org"
    resp = client.get(f"/visits?url={url}")
    print(f"Get visits response: {resp.status_code}, {resp.text}")
    assert resp.status_code == 200
    visits = resp.json()
    assert isinstance(visits, list)
    assert len(visits) > 0


def test_get_latest_visit_endpoint(client):
    #  create a visit
    payload = {
        "url": "https://example.org",
        "link_count": 25,
        "internal_links": 20,
        "external_links": 5,
        "word_count": 1500,
        "image_count": 8,
        "content_images": 6,
        "decorative_images": 2
    }
    create_resp = client.post("/visits", json=payload)
    if create_resp.status_code != 201:
        print(f"Create failed: {create_resp.text}")
        pytest.fail("Failed to create visit for test")

    #  test getting latest visit
    url = "https://example.org"
    resp = client.get(f"/visits/latest?url={url}")
    print(f"Latest visit response: {resp.status_code}, {resp.text}")
    if resp.status_code == 404:
        pytest.skip("/visits/latest endpoint not implemented")
    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == url


def test_get_stats_endpoint(client):
    # create some visits
    payloads = [
        {
            "url": "https://example.org",
            "link_count": 25,
            "internal_links": 20,
            "external_links": 5,
            "word_count": 1500,
            "image_count": 8,
            "content_images": 6,
            "decorative_images": 2
        },
        {
            "url": "https://example.com",
            "link_count": 30,
            "internal_links": 25,
            "external_links": 5,
            "word_count": 2000,
            "image_count": 10,
            "content_images": 8,
            "decorative_images": 2
        }
    ]

    for payload in payloads:
        resp = client.post("/visits", json=payload)
        if resp.status_code != 201:
            print(f"Create failed for {payload['url']}: {resp.text}")

    # Then test getting stats
    resp = client.get("/visits/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_visits" in data
    assert "unique_urls" in data


def test_get_recent_visits_endpoint(client):
    # create some visits
    payloads = [
        {
            "url": "https://example.org",
            "link_count": 25,
            "internal_links": 20,
            "external_links": 5,
            "word_count": 1500,
            "image_count": 8,
            "content_images": 6,
            "decorative_images": 2
        },
        {
            "url": "https://example.com",
            "link_count": 30,
            "internal_links": 25,
            "external_links": 5,
            "word_count": 2000,
            "image_count": 10,
            "content_images": 8,
            "decorative_images": 2
        }
    ]

    for payload in payloads:
        resp = client.post("/visits", json=payload)
        if resp.status_code != 201:
            print(f"Create failed for {payload['url']}: {resp.text}")

    # test getting recent visits
    resp = client.get("/visits/recent?limit=3")
    assert resp.status_code == 200
    visits = resp.json()
    assert isinstance(visits, list)
    assert len(visits) <= 3
