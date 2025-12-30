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
    import uvicorn
    import os
    from starlette.responses import JSONResponse
    from starlette.middleware.cors import CORSMiddleware

    port = int(os.environ.get("PORT", 10000))
    
    # 1. FastMCP에서 실제 작동하는 ASGI 앱을 꺼냅니다.
    app = mcp.as_asgi()

    # 2. CORS 및 모든 메서드(POST 포함) 허용 설정
    # PlayMCP가 정보를 긁어갈 때 발생하는 405 에러를 방지합니다.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. 루트(/) 경로 접속 시 200 OK 응답 추가 (PlayMCP 연결 확인용)
    @app.route("/")
    async def health_check(request):
        return JSONResponse({"status": "ok", "mcp_endpoint": "/sse"})

    logger.info(f"🚀 PlayMCP 연동 강화 모드 실행 (Port: {port})")
    
    # 4. uvicorn으로 직접 실행하여 포트 10000번에 앱을 고정합니다.
    uvicorn.run(app, host="0.0.0.0", port=port)