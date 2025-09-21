import httpx, os

BASE_URL = "https://ecos.bok.or.kr/api"

async def fetch_stat(stat_code, start_date, end_date):
    api_key = os.getenv("ECOS_API_KEY")
    url = f"{BASE_URL}/StatisticSearch/{api_key}/json/kr/1/100/{stat_code}/{start_date}/{end_date}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()
