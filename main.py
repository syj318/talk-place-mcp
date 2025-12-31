import os
from fastapi import FastAPI
from fastmcp import FastMCP

# ==================================================
# 1) REST API (PlayMCP 확인용)
# ==================================================
api = FastAPI()

@api.get("/")
def root():
    return {
        "status": "ok",
        "name": "TalkPlace MCP",
        "description": "MCP server for bookmarking places",
        "mcp_endpoint": "/sse"
    }

# ==================================================
# 2) MCP 서버 (카카오 가이드의 McpServer 역할)
# ==================================================
mcp = FastMCP(
    name="TalkPlace",
    instructions="Save and list places mentioned in conversation."
)

# ==================================================
# 3) Tool 구현 (카카오의 ToolSpec 대응)
# ==================================================
@mcp.tool()
def list_places(genre: str | None = None) -> str:
    """
    List saved places. Optionally filter by genre.
    """
    places = [
        {"name": "부산 카페", "genre": "CAFE"},
        {"name": "서울 맛집", "genre": "FOOD"},
        {"name": "제주 여행지", "genre": "TRAVEL"},
    ]

    if genre:
        places = [p for p in places if p["genre"] == genre]

    return {
        "count": len(places),
        "places": places
    }

@mcp.tool()
def recommend_place() -> str:
    """
    Recommend a random place.
    """
    return "🌟 오늘의 추천 장소: 부산 오션뷰 카페"

# ==================================================
# 4) 서버 실행 (Streamable HTTP / SSE)
# ==================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    mcp.run(
        host="0.0.0.0",
        port=port,
        transport="sse",
        path="/sse",
        app=api   # ← REST + MCP 결합 (중요)
    )
