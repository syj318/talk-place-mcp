from fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. MCP 서버 생성 (가장 기본형으로 생성해야 에러가 안 납니다)
mcp = FastMCP("TalkPlaceBookmark")

# 2. 구글 시트 설정
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    secret_path = "/etc/secrets/credentials.json"
    if not os.path.exists(secret_path):
        secret_path = "credentials.json"
    
    creds = Credentials.from_service_account_file(secret_path, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
    return client.open_by_key(sheet_id).sheet1

# 3. 도구(Tool) 정의
@mcp.tool()
async def save_place(place_name: str, context: str) -> str:
    """카톡 대화 장소를 구글 시트에 저장합니다."""
    try:
        sheet = get_sheet()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, place_name, context])
        return f"✅ '{place_name}' 저장 완료!"
    except Exception as e:
        logger.error(f"Save error: {e}")
        return f"❌ 저장 실패: {str(e)}"

@mcp.tool()
async def get_saved_places(keyword: str = "") -> str:
    """저장된 장소 목록을 불러옵니다."""
    try:
        sheet = get_sheet()
        rows = sheet.get_all_records()
        if not rows: return "저장된 장소가 없습니다."
        
        results = [r for r in rows if keyword in str(r)] if keyword else rows[-5:]
        text = "\n".join([f"- {r.get('장소명', '알수없음')} ({r.get('맥락(의도)', '내용없음')})" for r in results])
        return "📍 장소 리스트:\n" + text
    except Exception as e:
        logger.error(f"Read error: {e}")
        return f"❌ 조회 실패: {str(e)}"

# 4. 실행부 (Render 포트에 맞춰 SSE 실행)
if __name__ == "__main__":
    # Render는 PORT 환경변수를 통해 10000번 포트를 할당합니다.
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 MCP 서버 가동 (Port: {port})")
    
    # 에러 원인이었던 external_app 관련 코드를 모두 제거했습니다.
    # fastmcp는 run(transport="sse") 호출 시 내부적으로 웹 서버를 구동합니다.
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=port
    )