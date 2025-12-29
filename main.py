from mcp.server.fastmcp import FastMCP

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
    print(f"[저장 로그] 장소: {place_name} | 맥락: {context}")
    return f"✅ '{place_name}'을(를) '{context}' 목적으로 저장했습니다!"

# 모든 파라미터 제거하고 단순하게 실행
if __name__ == "__main__":
    mcp.run()