from mcp.server.fastmcp import FastMCP
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime

# 1. MCP 및 구글 시트 설정
mcp = FastMCP("TalkPlaceBookmark")

SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    # Render의 Secret Files에 등록한 credentials.json 사용
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPE)
    client = gspread.authorize(creds)
    # 반드시 본인의 시트 ID로 수정하세요!
    return client.open_by_key("1M0VZMN6vEjZY_uh58-04K1W9bB5CgLbn40dx_I_5UBw").sheet1

# [기능 1] 장소 저장 도구
@mcp.tool()
async def save_place(place_name: str, context: str):
    """카톡 대화 장소를 구글 시트에 저장합니다."""
    try:
        sheet = get_sheet()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, place_name, context])
        return f"✅ '{place_name}' 저장 완료! (구글 시트 확인)"
    except Exception as e:
        return f"❌ 저장 실패: {str(e)}"

# [기능 2] 저장된 장소 조회 도구 (새로 추가됨!)
@mcp.tool()
async def get_saved_places(keyword: str = ""):
    """
    저장된 장소 목록을 불러옵니다. 
    keyword가 있으면 해당 키워드(장소명이나 맥락)가 포함된 곳만 찾습니다.
    """
    try:
        sheet = get_sheet()
        all_records = sheet.get_all_records() # 시트의 모든 데이터를 가져옴
        
        if not all_records:
            return "아직 저장된 장소가 없습니다."

        if keyword:
            # 키워드로 검색 (장소명이나 맥락에 포함된 경우)
            filtered = [r for r in all_records if keyword in r['장소명'] or keyword in r['맥락(의도)']]
            if not filtered:
                return f"🔍 '{keyword}'와 관련된 장소를 찾지 못했습니다."
            results = filtered
        else:
            # 키워드 없으면 최근 5개만 출력
            results = all_records[-5:]

        message = "📍 저장된 장소 리스트입니다:\n"
        for r in results:
            message += f"- {r['장소명']} ({r['맥락(의도)']})\n"
        
        return message
    except Exception as e:
        return f"❌ 조회 실패: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
# FastMCP의 run()은 내부적으로 uvicorn을 실행하며, 
# 필요한 설정은 기본적으로 포트만 명시해도 Render 환경에서 잘 작동합니다.
mcp.run()