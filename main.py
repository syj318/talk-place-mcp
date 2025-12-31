from fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import logging
import uvicorn
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from starlette.routing import Route, Mount

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP 서버 생성
mcp = FastMCP("TalkPlaceBookmark")

SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    secret_path = "/etc/secrets/credentials.json"
    if not os.path.exists(secret_path):
        secret_path = "credentials.json"
    creds = Credentials.from_service_account_file(secret_path, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
    return client.open_by_key(sheet_id).sheet1

@mcp.tool()
async def save_place(place_name: str, context: str) -> str:
    """카톡 대화 장소를 구글 시트에 저장합니다."""
    sheet = get_sheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, place_name, context])
    return f"✅ '{place_name}' 저장 완료!"

@mcp.tool()
async def get_saved_places(keyword: str = "") -> str:
    """저장된 장소 목록을 불러옵니다."""
    sheet = get_sheet()
    rows = sheet.get_all_records()
    if not rows: return "저장된 장소가 없습니다."
    results = [r for r in rows if keyword in str(r)] if keyword else rows[-5:]
    text = "\n".join([f"- {r.get('장소명')} ({r.get('맥락(의도)')})" for r in results])
    return "📍 장소 리스트:\n" + text

# --- PlayMCP 연동을 위한 서버 실행부 ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # 1. FastMCP 앱 추출
    try:
        mcp_app = mcp.as_asgi()
    except AttributeError:
        mcp_app = mcp._app

    # 2. 루트(/) 경로 접속 시 응답 (PlayMCP 연결 확인용)
    async def homepage(request):
        return JSONResponse({"status": "ok", "mcp_endpoint": "/sse"})

    # 3. 통합 앱 구성
    routes = [
        Route("/", endpoint=homepage),
        Mount("/", app=mcp_app)
    ]
    app = Starlette(routes=routes)

    logger.info(f"🚀 PlayMCP 연동 모드 시작 (Port: {port})")
    uvicorn.run(app, host="0.0.0.0", port=port)