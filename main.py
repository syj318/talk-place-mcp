from fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("TalkPlaceBookmark")
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    try:
        # Render Secret Files 경로 확인
        secret_path = '/etc/secrets/credentials.json'
        if not os.path.exists(secret_path):
            secret_path = 'credentials.json'
            
        if not os.path.exists(secret_path):
            logger.error("❌ 인증 파일을 찾을 수 없습니다.")
            raise FileNotFoundError("credentials.json missing")

        creds = Credentials.from_service_account_file(secret_path, scopes=SCOPE)
        client = gspread.authorize(creds)
        sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        logger.error(f"❌ 시트 연결 실패: {str(e)}")
        raise e

@mcp.tool()
async def save_place(place_name: str, context: str):
    """카톡 대화 장소를 구글 시트에 저장합니다."""
    try:
        sheet = get_sheet()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, place_name, context])
        return f"✅ '{place_name}' 저장 완료!"
    except Exception as e:
        return f"❌ 저장 실패: {str(e)}"

@mcp.tool()
async def get_saved_places(keyword: str = ""):
    """저장된 장소 목록을 불러옵니다."""
    try:
        sheet = get_sheet()
        all_records = sheet.get_all_records()
        if not all_records: return "저장된 장소가 없습니다."
        results = [r for r in all_records if keyword in r.get('장소명', '') or keyword in r.get('맥락(의도)', '')] if keyword else all_records[-5:]
        return "📍 장소 리스트:\n" + "\n".join([f"- {r.get('장소명')} ({r.get('맥락(의도)')})" for r in results])
    except Exception as e:
        return f"❌ 조회 실패: {str(e)}"

if __name__ == "__main__":
    import os
    # Render는 PORT 환경 변수를 제공합니다.
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 서버 시작 (Port: {port})")
    
    # transport를 "sse"로 바꿔야 카카오톡(PlayMCP)과 연결됩니다.
    mcp.run(transport="sse", host="0.0.0.0", port=port)