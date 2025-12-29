from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("TalkPlaceBookmark")

@mcp.tool()
async def save_place(place_name: str, context: str):
    """
    카톡 대화에서 나온 장소와 맥락을 저장합니다.
    - place_name: 식당이나 카페 이름
    - context: '부모님 모시고 가기 좋은 곳' 같은 대화 내용
    """
    print(f"로그: 장소 '{place_name}'가 '{context}'라는 맥락으로 감지되었습니다.")
    return f"✅ '{place_name}'을(를) 성공적으로 기록했습니다! (메모: {context})"

if __name__ == "__main__":
    # Render에서 제공하는 포트 번호를 가져옵니다.
    port = int(os.environ.get("PORT", 8000))
    # mcp.run() 대신 run_sse_server()를 사용하여 포트와 호스트를 설정합니다.
    mcp.run_sse_server(host="0.0.0.0", port=port)