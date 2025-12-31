from fastapi import FastAPI
from fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# 1️⃣ FastAPI 앱
app = FastAPI()

# 2️⃣ MCP 생성
mcp = FastMCP("TalkPlaceBookmark")

# 3️⃣ PlayMCP가 처음 확인하는 루트
@app.get("/")
def root():
    return {
        "name": "TalkPlaceBookmark",
        "transport": "sse",
        "status": "ok"
    }

# 4️⃣ MCP 툴 등록
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    path = "/etc/secrets/credentials.json"
    if not os.path.exists(path):
        path = "credentials.json"

    creds = Credentials.from_service_account_file(path, scopes=SCOPE)
    client = gspread.authorize(creds)
    return client.open_by_key(
        "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
    ).sheet1

@mcp.tool()
async def save_place(place_name: str, context: str):
    sheet = get_sheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, place_name, context])
    return f"✅ '{place_name}' 저장 완료"

@mcp.tool()
async def get_saved_places(keyword: str = ""):
    sheet = get_sheet()
    rows = sheet.get_all_records()
    return rows[-5:]

# 5️⃣ 🔥 핵심: MCP를 FastAPI에 마운트
app.mount("/", mcp.app)

