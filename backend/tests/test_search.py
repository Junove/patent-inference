def test_search_by_keyword(client, patent_repo):
    r = client.get("/api/v1/patents/search", params={"q": "battery"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert any(p["id"] == "US9999001" for p in body["results"])


def test_search_filter_only_no_keyword(client, patent_repo):
    r = client.get("/api/v1/patents/search", params={"assignee": "Northwind Labs"})
    results = r.json()["results"]
    assert results and all(p["id"] == "US9999002" for p in results)


def test_patent_detail_includes_cited_patents(client, patent_repo):
    r = client.get("/api/v1/patents/US9999002")
    assert r.status_code == 200
    body = r.json()
    assert body["claims"] == ["1. A pad comprising a coil."]
    assert body["cited_patents"][0]["id"] == "US9999001"


def test_search_date_and_classification_filters(client, patent_repo):
    r = client.get("/api/v1/patents/search", params={"date_to": "2023-12-31"})
    assert r.json()["results"] and all(p["id"] == "US9999002" for p in r.json()["results"])

    r = client.get("/api/v1/patents/search", params={"classification": "H01M"})
    assert r.json()["results"] and all(p["id"] == "US9999001" for p in r.json()["results"])


def test_patent_not_found(client, patent_repo):
    r = client.get("/api/v1/patents/does-not-exist")
    assert r.status_code == 404 and r.json()["code"] == "not_found"
