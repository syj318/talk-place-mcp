from mcp.server.fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime

# 1. MCP 및 구글 시트 설정
mcp = FastMCP("TalkPlaceBookmark")

# 구글 인증 정보 설정 (환경 변수 사용 권장)
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    # Render의 Environment Variables에 저장한 JSON 경로 혹은 내용을 불러옵니다.
    # 테스트를 위해 파일명을 'credentials.json'으로 두겠습니다.
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPE)
    client = gspread.authorize(creds)
    # 아까 복사한 시트 ID를 입력하세요.
    return client.open_by_key("1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw").sheet1

# 2. 장소 저장 도구 수정
@mcp.tool()
async def save_place(place_name: str, context: str):
    """카톡 대화 장소를 구글 시트에 저장합니다."""
    try:
        sheet = get_sheet()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 구글 시트에 한 줄 추가
        sheet.append_row([now, place_name, context])
        return f"✅ '{place_name}' 저장 완료! (구글 시트 확인)"
    except Exception as e:
        return f"❌ 저장 실패: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="sse", host="0.0.0.0", port=port)