from mcp.server.fastmcp import FastMCP
import uvicorn
import os

mcp = FastMCP("TalkPlaceBookmark")

@mcp.tool()
async def save_place(place_name: str, context: str):
    print(f"[저장 로그] 장소: {place_name} | 맥락: {context}")
    return f"✅ '{place_name}'을(를) '{context}' 목적으로 저장했습니다!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    # ⭐ 핵심: mcp.app을 uvicorn으로 직접 실행
    uvicorn.run(
        mcp.app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
