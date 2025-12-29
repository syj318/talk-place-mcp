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
    # 서버 로그에서 확인 가능하도록 출력
    print(f"[저장 로그] 장소: {place_name} | 맥락: {context}")
    return f"✅ '{place_name}'을(를) '{context}' 목적으로 저장했습니다!"

if __name__ == "__main__":
    # Render는 'PORT' 환경 변수를 통해 포트를 할당합니다.
    # 포트 정보가 없으면 기본값으로 8000을 사용합니다.
    port = int(os.environ.get("PORT", 8000))
    
    # 중요: host를 "0.0.0.0"으로 설정해야 외부(Render 부하 분산기)에서 접속이 가능합니다.
    mcp.run(transport="sse", host="0.0.0.0", port=port)