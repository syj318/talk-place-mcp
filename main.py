from mcp.server.fastmcp import FastMCP

# 1. MCP 서버 이름 설정
mcp = FastMCP("TalkPlaceBookmark")

# 2. 장소 저장 도구 (Tool) 만들기
@mcp.tool()
async def save_place(place_name: str, context: str):
    """
    카톡 대화에서 나온 장소와 맥락을 저장합니다.
    - place_name: 식당이나 카페 이름
    - context: '부모님 모시고 가기 좋은 곳' 같은 대화 내용
    """
    # 지금은 테스트용으로 화면에 출력만 합니다.
    print(f"로그: 장소 '{place_name}'가 '{context}'라는 맥락으로 감지되었습니다.")
    return f"✅ '{place_name}'을(를) 성공적으로 기록했습니다! (메모: {context})"

# 3. 서버 실행
if __name__ == "__main__":
    import os
    # Render는 포트 번호를 환경 변수로 제공합니다.
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="sse", port=port, host="0.0.0.0")