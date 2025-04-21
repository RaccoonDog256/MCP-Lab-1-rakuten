from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rakuten")

RAKUTEN_API_BASE = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
# 以下に楽天APIのアプリIDを設定してください。
APPLICATION_ID = ""
USER_AGENT = "rakuten-app/1.0"

# 🎯 許可されたsort値一覧（楽天API公式）
ALLOWED_SORT_VALUES = {
    "standard",
    "+affiliateRate", "-affiliateRate",
    "+reviewCount", "-reviewCount",
    "+reviewAverage", "-reviewAverage",
    "+itemPrice", "-itemPrice",
    "+updateTimestamp", "-updateTimestamp",
}

# 🔧 パラメータでAPI叩く（sortも安全に）
async def make_rakuten_request(params: dict[str, Any]) -> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT
    }
    params["applicationId"] = APPLICATION_ID
    params["format"] = "json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(RAKUTEN_API_BASE, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None

# 🛍️ MCPツール本体：sortバリデーション・可変パラメータ対応
@mcp.tool()
async def search_items(
    keyword: str,
    sort: str = "",
    minPrice: int = 0,
    maxPrice: int = 0,
    availability: int = 0
) -> str:
    """楽天市場で商品検索を行う"""

    # 🔒 sortバリデーション（無効ならエラー返す）
    if sort and sort not in ALLOWED_SORT_VALUES:
        return f"`sort` に無効な値が指定されています：{sort} \n有効な値は: {', '.join(ALLOWED_SORT_VALUES)}"

    # 📦 パラメータ準備
    params = {
        "keyword": keyword,
    }
    if sort:
        params["sort"] = sort
    if minPrice > 0:
        params["minPrice"] = minPrice
    if maxPrice > 0:
        params["maxPrice"] = maxPrice
    if availability in (0, 1):
        params["availability"] = availability

    data = await make_rakuten_request(params)

    if not data or "Items" not in data or not data["Items"]:
        return "指定した条件に合う商品が見つかりませんでした"

    items = data["Items"][:5]
    results = []
    for item in items:
        i = item["Item"]
        result = f"{i['itemName']} - {i['itemPrice']}円\n{i['itemUrl']}"
        results.append(result)

    return "\n---\n".join(results)

# 🚀 起動エントリーポイント
if __name__ == "__main__":
    mcp.run(transport="stdio")
