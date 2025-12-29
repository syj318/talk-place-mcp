from mcp.server.fastmcp import FastMCP

# 1. MCP 서버 초기화
mcp = FastMCP("TalkPlaceBookmark")

# 2. 핵심: Uvicorn이 인식할 수 있도록 내부 ASGI 앱을 'app' 변수에 할당
# FastMCP 객체 내부의 실제 웹 서버 엔진을 밖으로 꺼내주는 작업입니다.
app = mcp.app

# 3. 장소 저장 도구 (Tool) 정의
@mcp.tool()
async def save_place(place_name: str, context: str):
    """
    카톡 대화에서 나온 장소와 방문 의도를 저장합니다.
    - place_name: 식당, 카페, 장소의 이름
    - context: '부모님과 갈 곳', '친구와 회식' 등 사용자의 대화 맥락
    """
    print(f"[저장 로그] 장소: {place_name} | 맥락: {context}")
    return f"✅ '{place_name}'을(를) '{context}' 목적으로 저장했습니다!"