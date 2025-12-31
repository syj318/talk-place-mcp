import os
from fastmcp import FastMCP

# 1. FastMCP 초기화 (생성자에는 name만 넣습니다)
mcp = FastMCP("TalkPlaceBookmark")

# 2. PlayMCP 등록을 위한 상태 확인용 루트 경로 (404 방지)
@mcp.external_app.get("/")
async def root():
    return {
        "status": "online",
        "server": "TalkPlaceBookmark",
        "endpoint": "/sse"
    }

# --- 여기에 기존에 작성하셨던 @mcp.tool 이나 @mcp.resource 코드들을 넣으세요 ---

# 예시용 도구 (기존 코드가 있다면 그대로 유지하세요)
@mcp.tool()
async def get_bookmark_status():
    """북마크 서버의 상태를 확인합니다."""
    return "Server is running perfectly!"

# ------------------------------------------------------------------

# 3. 실행부 (Render의 포트 10000번에 맞춰 SSE로 실행)
if __name__ == "__main__":
    # Render는 기본적으로 PORT 환경변수를 10000으로 제공합니다.
    port = int(os.environ.get("PORT", 10000))
    
    # run() 메서드에서 transport를 지정하거나 기본값을 사용합니다.
    # 포트 설정을 위해 host와 port를 명시합니다.
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=port
    )