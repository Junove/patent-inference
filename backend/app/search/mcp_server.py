"""MCP tool wrapper for patent search (FR-S4): same two operations as the HTTP
API, for the generator and external agents. Run standalone: python -m app.search.mcp_server"""
from mcp.server.mcpserver import MCPServer

from app.search.deps import get_patent_repository

mcp = MCPServer("patent-search")


@mcp.tool()
def search_patents(q: str, page: int = 1, date_from: str | None = None, date_to: str | None = None,
                    assignee: str | None = None, inventor: str | None = None, classification: str | None = None) -> dict:
    """Keyword search over patent title, abstract, claims and inventors."""
    results, total = get_patent_repository().search(
        q, page=page, date_from=date_from, date_to=date_to, assignee=assignee, inventor=inventor,
        classification=classification,
    )
    return {"results": [r.model_dump() for r in results], "total": total}


@mcp.tool()
def get_patent(patent_id: str) -> dict | None:
    """Full patent record: text, claims and cited patents."""
    detail = get_patent_repository().get(patent_id)
    return detail.model_dump() if detail else None


if __name__ == "__main__":
    mcp.run()
