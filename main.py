# from fastapi import FastAPI

# app = FastAPI()

# from pydantic import BaseModel
# import gspread
# from google.oauth2.service_account import Credentials
# import os
# from datetime import datetime


# SCOPE = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive"
# ]

# # --- Google Sheet 연결 ---
# def get_sheet():
#     secret_path = "/etc/secrets/credentials.json"
#     if not os.path.exists(secret_path):
#         secret_path = "credentials.json"

#     creds = Credentials.from_service_account_file(
#         secret_path, scopes=SCOPE
#     )
#     client = gspread.authorize(creds)
#     sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
#     return client.open_by_key(sheet_id).sheet1


# # ✅ PlayMCP가 제일 먼저 찌르는 엔드포인트
# @app.get("/")
# def root():
#     return {
#         "name": "TalkPlaceBookmark",
#         "status": "ok"
#     }


# # ✅ PlayMCP 필수: tool 목록
# @app.post("/tools/list")
# def list_tools():
#     return {
#         "tools": [
#             {
#                 "name": "save_place",
#                 "description": "카톡 대화에서 나온 장소를 저장합니다",
#                 "input_schema": {
#                     "type": "object",
#                     "properties": {
#                         "place_name": {"type": "string"},
#                         "context": {"type": "string"}
#                     },
#                     "required": ["place_name", "context"]
#                 }
#             },
#             {
#                 "name": "get_saved_places",
#                 "description": "저장된 장소 목록을 불러옵니다",
#                 "input_schema": {
#                     "type": "object",
#                     "properties": {
#                         "keyword": {"type": "string"}
#                     }
#                 }
#             }
#         ]
#     }


# class ToolCall(BaseModel):
#     name: str
#     arguments: dict


# # ✅ tool 실행
# @app.post("/tools/call")
# def call_tool(call: ToolCall):
#     sheet = get_sheet()

#     if call.name == "save_place":
#         now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         place = call.arguments["place_name"]
#         context = call.arguments["context"]

#         sheet.append_row([now, place, context])
#         return {"result": f"✅ '{place}' 저장 완료"}

#     if call.name == "get_saved_places":
#         keyword = call.arguments.get("keyword", "")
#         rows = sheet.get_all_records()

#         results = [
#             r for r in rows
#             if keyword in r.get("장소명", "") or keyword in r.get("맥락(의도)", "")
#         ] if keyword else rows[-5:]

#         text = "\n".join(
#             f"- {r['장소명']} ({r['맥락(의도)']})" for r in results
#         )

#         return {"result": "📍 장소 리스트\n" + text}

#     return {"error": "Unknown tool"}

from fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import logging
import uvicorn
from starlette.middleware.cors import CORSMiddleware

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("TalkPlaceBookmark")
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    try:
        secret_path = '/etc/secrets/credentials.json'
        if not os.path.exists(secret_path):
            secret_path = 'credentials.json'
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
    sheet = get_sheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, place_name, context])
    return f"✅ '{place_name}' 저장 완료!"

@mcp.tool()
async def get_saved_places(keyword: str = ""):
    """저장된 장소 목록을 불러옵니다."""
    sheet = get_sheet()
    all_records = sheet.get_all_records()
    if not all_records: return "저장된 장소가 없습니다."
    results = [r for r in all_records if keyword in str(r)] if keyword else all_records[-5:]
    return "📍 장소 리스트:\n" + "\n".join([f"- {r.get('장소명')} ({r.get('맥락(의도)')})" for r in results])
if __name__ == "__main__":
    import os
    # Render가 할당하는 포트 번호를 가져옵니다.
    port = int(os.environ.get("PORT", 10000))
    
    logger.info(f"🚀 MCP 서버 가동 시작 (Port: {port})")
    
    # 억지로 app을 추출하지 않고 공식 run 메서드를 사용합니다.
    # transport="sse"는 PlayMCP 연동을 위한 필수 설정입니다.
    # host="0.0.0.0"은 외부(Render)에서 접속할 수 있게 문을 여는 설정입니다.
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=port
    )