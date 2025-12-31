from fastapi import FastAPI
from fastmcp import FastMCP
import uvicorn

# =========================
# 1. MCP 서버 생성 (SSE)
# =========================
mcp = FastMCP(
    name="TalkPlaceBookmark",
    transport="sse",
)

# =========================
# 2. MCP Tool 정의
# =========================
@mcp.tool()
def save_place(place_name: str, context: str) -> str:
    """
    장소를 북마크로 저장합니다.
    """
    return f"📌 '{place_name}' 저장 완료 (상황: {context})"


@mcp.tool()
def list_places() -> list:
    """
    저장된 장소 목록을 반환합니다.
    """
    return ["부산 카페", "서울 맛집", "제주 여행지"]


# =========================
# 3. FastAPI (PlayMCP용)
# =========================
app = FastAPI(title="TalkPlace MCP Bridge")

@app.get("/")
def health_check():
    """
    PlayMCP '정보 불러오기' 통과용
    """
    return {
        "status": "ok",
        "service": "TalkPlaceBookmark MCP",
        "transport": "SSE",
        "sse_endpoint": "/sse"
    }


# =========================
# 4. MCP 서버 마운트
# =========================
# ⚠️ 공식 방식: mcp.server.app
app.mount("/", mcp.server.app)


# =========================
# 5. 실행 (Render 호환)
# =========================
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=10000,
    )
