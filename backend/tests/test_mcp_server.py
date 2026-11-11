def test_mcp_tools_expose_search_and_get(client, patent_repo):
    from app.search.mcp_server import get_patent, mcp, search_patents

    assert mcp.name == "patent-search"
    found = search_patents("battery")
    assert found["total"] >= 1 and any(p["id"] == "US9999001" for p in found["results"])
    assert get_patent("US9999001")["title"] == "Solid-state battery electrolyte"
    assert get_patent("nope") is None
