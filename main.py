from fastapi import FastAPI

app = FastAPI()

from pydantic import BaseModel
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime

app = FastAPI()

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --- Google Sheet 연결 ---
def get_sheet():
    secret_path = "/etc/secrets/credentials.json"
    if not os.path.exists(secret_path):
        secret_path = "credentials.json"

    creds = Credentials.from_service_account_file(
        secret_path, scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
    return client.open_by_key(sheet_id).sheet1


# ✅ PlayMCP가 제일 먼저 찌르는 엔드포인트
@app.get("/")
def root():
    return {
        "name": "TalkPlaceBookmark",
        "status": "ok"
    }


# ✅ PlayMCP 필수: tool 목록
@app.post("/tools/list")
def list_tools():
    return {
        "tools": [
            {
                "name": "save_place",
                "description": "카톡 대화에서 나온 장소를 저장합니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "place_name": {"type": "string"},
                        "context": {"type": "string"}
                    },
                    "required": ["place_name", "context"]
                }
            },
            {
                "name": "get_saved_places",
                "description": "저장된 장소 목록을 불러옵니다",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"}
                    }
                }
            }
        ]
    }


class ToolCall(BaseModel):
    name: str
    arguments: dict


# ✅ tool 실행
@app.post("/tools/call")
def call_tool(call: ToolCall):
    sheet = get_sheet()

    if call.name == "save_place":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        place = call.arguments["place_name"]
        context = call.arguments["context"]

        sheet.append_row([now, place, context])
        return {"result": f"✅ '{place}' 저장 완료"}

    if call.name == "get_saved_places":
        keyword = call.arguments.get("keyword", "")
        rows = sheet.get_all_records()

        results = [
            r for r in rows
            if keyword in r.get("장소명", "") or keyword in r.get("맥락(의도)", "")
        ] if keyword else rows[-5:]

        text = "\n".join(
            f"- {r['장소명']} ({r['맥락(의도)']})" for r in results
        )

        return {"result": "📍 장소 리스트\n" + text}

    return {"error": "Unknown tool"}
