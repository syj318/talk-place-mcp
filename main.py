from mcp.server.fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import logging

# 로그 설정 (Render 대시보드에서 에러를 확인하기 위함)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("TalkPlaceBookmark")

SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    try:
        # 1. Render Secret Files의 절대 경로를 직접 지정합니다.
        # 이 경로가 아니면 Render 서버에서 파일을 찾지 못합니다.
        secret_path = '/etc/secrets/credentials.json'
        
        # 2. 로컬 테스트 환경을 위한 예외 처리
        if not os.path.exists(secret_path):
            secret_path = 'credentials.json'
            
        logger.info(f"인증 파일 경로 사용 중: {secret_path}")
        
        # 파일이 실제로 있는지 최종 확인
        if not os.path.exists(secret_path):
            raise FileNotFoundError(f"인증 파일을 찾을 수 없습니다: {secret_path}")

        creds = Credentials.from_service_account_file(secret_path, scopes=SCOPE)
        client = gspread.authorize(creds)
        
        # 사용자님의 시트 ID
        sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        logger.error(f"시트 연결 실패 에러 상세: {str(e)}")
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
    # Render 환경 변수에서 포트를 가져오고 SSE 방식으로 명시적 실행
    port = int(os.environ.get("PORT", 10000))
    mcp.run(transport="sse", host="0.0.0.0", port=port)