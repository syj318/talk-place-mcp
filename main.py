from mcp.server.fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import logging

# 에러 확인을 위한 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. MCP 설정
mcp = FastMCP("TalkPlaceBookmark")

SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    try:
        # 현재 실행 파일(main.py)이 있는 위치를 기준으로 경로를 잡습니다.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        creds_path = os.path.join(current_dir, 'credentials.json')
        
        # 파일이 실제로 존재하는지 체크 (로그 확인용)
        if not os.path.exists(creds_path):
            logger.error(f"파일을 찾을 수 없습니다: {creds_path}")
            raise FileNotFoundError(f"credentials.json missing at {creds_path}")

        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPE)
        client = gspread.authorize(creds)
        
        sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        logger.error(f"시트 연결 중 오류 발생: {str(e)}")
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
        
        results = [r for r in all_records if keyword in r['장소명'] or keyword in r['맥락(의도)']] if keyword else all_records[-5:]
        msg = "📍 저장된 장소 리스트:\n" + "\n".join([f"- {r['장소명']} ({r['맥락(의도)']})" for r in results])
        return msg
    except Exception as e:
        return f"❌ 조회 실패: {str(e)}"

if __name__ == "__main__":
    # Render 환경에서 가장 안정적인 실행 방식입니다.
    mcp.run()