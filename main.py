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

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. MCP 서버 객체 생성 (PlayMCP가 인식하는 표준)
mcp = FastMCP("TalkPlaceBookmark")

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    # Render Secret Files 경로 또는 로컬 경로 확인
    secret_path = "/etc/secrets/credentials.json"
    if not os.path.exists(secret_path):
        secret_path = "credentials.json"

    creds = Credentials.from_service_account_file(secret_path, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
    return client.open_by_key(sheet_id).sheet1

# ✅ 도구 1: 장소 저장
@mcp.tool()
async def save_place(place_name: str, context: str) -> str:
    """카톡 대화에서 나온 장소 정보를 구글 시트에 저장합니다."""
    try:
        sheet = get_sheet()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 시트 헤더가 [일시, 장소명, 맥락(의도)] 순서라고 가정합니다.
        sheet.append_row([now, place_name, context])
        return f"✅ '{place_name}' 저장 완료!"
    except Exception as e:
        logger.error(f"저장 에러: {e}")
        return f"❌ 저장 실패: {str(e)}"

# ✅ 도구 2: 목록 조회
@mcp.tool()
async def get_saved_places(keyword: str = "") -> str:
    """저장된 장소 목록을 불러옵니다. 키워드로 검색이 가능합니다."""
    try:
        sheet = get_sheet()
        rows = sheet.get_all_records()
        
        if not rows:
            return "저장된 장소가 없습니다."

        results = [
            r for r in rows
            if keyword in str(r.get("장소명", "")) or keyword in str(r.get("맥락(의도)", ""))
        ] if keyword else rows[-5:]

        if not results:
            return f"🔍 '{keyword}'와 관련된 장소를 찾지 못했습니다."

        text = "\n".join(f"- {r.get('장소명')} ({r.get('맥락(의도)')})" for r in results)
        return "📍 최근 저장된 장소 리스트:\n" + text
    except Exception as e:
        logger.error(f"조회 에러: {e}")
        return f"❌ 조회 실패: {str(e)}"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    # PlayMCP와의 통신을 위해 SSE(Server-Sent Events) 방식으로 실행
    mcp.run(transport="sse", host="0.0.0.0", port=port)