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
    # Render는 PORT 환경 변수를 통해 포트를 지정합니다.
    port = int(os.environ.get("PORT", 8000))
    
    # 최신 버전의 FastMCP는 mcp.run()에 직접 port를 넣지 않고 
    # 아래와 같이 transport 설정만으로 충분하거나, 환경에 따라 설정을 조정합니다.
    # 인자 없이 실행해도 transport="sse" 시 내부 서버가 가동됩니다.
    mcp.run(transport="sse")