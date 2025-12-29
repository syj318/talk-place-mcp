from mcp.server.fastmcp import FastMCP
import os

# 1. MCP 서버 초기화
mcp = FastMCP("TalkPlaceBookmark")

# 2. 장소 저장 도구 (Tool) 정의
@mcp.tool()
async def save_place(place_name: str, context: str):
    """
    카톡 대화에서 나온 장소와 방문 의도를 저장합니다.
    - place_name: 식당, 카페, 장소의 이름
    - context: 사용자의 대화 맥락 (예: 부모님과 갈 곳)
    """
    print(f"[저장 로그] 장소: {place_name} | 맥락: {context}")
    return f"✅ '{place_name}'을(를) '{context}' 목적으로 저장했습니다!"

if __name__ == "__main__":
    # Render가 할당하는 포트를 가져옵니다.
    port = int(os.environ.get("PORT", 8000))
    
    # mcp.run()에 transport="sse"만 넣으면 
    # 라이브러리가 내부적으로 포트와 호스트를 자동으로 잡으려 시도합니다.
    mcp.run(transport="sse")