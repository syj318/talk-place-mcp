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
        # 1. Render Secret Files의 절대 경로를 먼저 확인합니다.
        secret_path = '/etc/secrets/credentials.json'
        
        # 2. 만약 해당 경로에 파일이 없다면(로컬 환경 등) 현재 폴더에서 찾습니다.
        if not os.path.exists(secret_path):
            secret_path = 'credentials.json'
            
        logger.info(f"인증 파일 경로 사용 중: {secret_path}")
        
        # 파일 존재 여부 최종 확인
        if not os.path.exists(secret_path):
            raise FileNotFoundError(f"인증 파일을 찾을 수 없습니다: {secret_path}")

        creds = Credentials.from_service_account_file(secret_path, scopes=SCOPE)
        client = gspread.authorize(creds)
        
        # 주소창에서 복사하신 시트 ID
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
    import os
    # Render가 부여하는 포트 번호를 읽어옵니다.
    port = int(os.environ.get("PORT", 10000))
    
    # SSE 전송 방식을 사용하며, 지정된 포트로 서버를 실행합니다.
    # 이 설정이 있어야 'No open ports detected' 에러가 사라집니다.
    mcp.run(transport="sse", host="0.0.0.0", port=port)