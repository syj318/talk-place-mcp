from mcp.server.fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("TalkPlaceBookmark")

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    try:
        secret_path = "/etc/secrets/credentials.json"
        if not os.path.exists(secret_path):
            secret_path = "credentials.json"

        logger.info(f"Using credentials file: {secret_path}")
        creds = Credentials.from_service_account_file(secret_path, scopes=SCOPE)
        client = gspread.authorize(creds)

        sheet_id = "1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw"
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        logger.error(f"시트 연결 실패: {e}")
        raise

@mcp.tool()
async def save_place(place_name: str, context: str):
    try:
        sheet = get_sheet()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, place_name, context])
        return f"✅ '{place_name}' 저장 완료!"
    except Exception as e:
        return f"❌ 저장 실패: {str(e)}"

@mcp.tool()
async def get_saved_places(keyword: str = ""):
    try:
        sheet = get_sheet()
        rows = sheet.get_all_records()
        if not rows:
            return "저장된 장소가 없습니다."

        results = (
            [r for r in rows if keyword in r["장소명"] or keyword in r["맥락(의도)"]]
            if keyword else rows[-5:]
        )

        return "📍 저장된 장소:\n" + "\n".join(
            f"- {r['장소명']} ({r['맥락(의도)' ]})" for r in results
        )
    except Exception as e:
        return f"❌ 조회 실패: {str(e)}"

# 🔥 여기가 핵심
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(
        host="0.0.0.0",
        port=port
    )
