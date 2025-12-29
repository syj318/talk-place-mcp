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
    - context: '부모님과 갈 곳', '친구와 회식' 등 사용자의 대화 맥락
    """
    # 서버 로그에서 확인 가능하도록 출력
    print(f"[저장 로그] 장소: {place_name} | 맥락: {context}")
    return f"✅ '{place_name}'을(를) '{context}' 목적으로 저장했습니다!"

if __name__ == "__main__":
    # 최신 버전의 FastMCP는 mcp.run() 호출 시 
    # transport="sse"만 지정하면 환경 변수 PORT를 자동으로 감지하여 실행됩니다.
    mcp.run(transport="sse")