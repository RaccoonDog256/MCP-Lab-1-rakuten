from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# FastMCP サーバーの初期化
# 元: mcp = FastMCP("weather")
mcp = FastMCP("rakuten")  # 楽天用に変更

# 定数
# 元: NWS_API_BASE = "https://api.weather.gov"
RAKUTEN_API_BASE = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"  # 楽天APIのURLに変更

# 以下に楽天APIのアプリIDを設定してください。
APPLICATION_ID = ""

# 元: USER_AGENT = "weather-app/1.0"
USER_AGENT = "rakuten-app/1.0"  # ユーザーエージェントを楽天用に変更

# 楽天APIへリクエストを送信する非同期関数（キーワードのみ使用）
# 元: make_nws_request で URL を直接受け取っていた
async def make_rakuten_request(keyword: str) -> dict[str, Any] | None:  # キーワードベースのAPI呼び出しに変更
    headers = {
        "User-Agent": USER_AGENT
    }
    params = {
        "applicationId": APPLICATION_ID,
        "keyword": keyword,
        "format": "json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(RAKUTEN_API_BASE, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

# 楽天市場の商品を検索するツール関数
# 元: get_alerts や get_forecast など天気に関する関数を削除し、楽天商品検索関数を追加
@mcp.tool()
async def search_items(keyword: str) -> str:
    """楽天市場でキーワード検索を行う。

    Args:
        keyword: 検索したいキーワード（例："ごみ箱"）
    """
    data = await make_rakuten_request(keyword)

    if not data or "Items" not in data or not data["Items"]:
        return "指定したキーワードの商品が見つかりませんでした。"

    items = data["Items"][:5]  # 最大5件まで表示
    results = []
    for item in items:
        i = item["Item"]
        result = f"{i['itemName']} - {i['itemPrice']}円\n{i['itemUrl']}"
        results.append(result)

    return "\n---\n".join(results)

# エントリーポイント（標準入出力でサーバーを起動）
if __name__ == "__main__":
    mcp.run(transport='stdio')