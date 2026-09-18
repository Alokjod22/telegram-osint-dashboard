import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class NewsWebAdapter:
    """OSINT adapter for searching news articles and web content."""

    @staticmethod
    async def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results = []
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a_tag in soup.find_all("a", class_="result__url", limit=max_results):
                        title_tag = a_tag.find_parent("div", class_="result__body")
                        title = title_tag.find("a", class_="result__a").text if title_tag else "No Title"
                        snippet = title_tag.find("a", class_="result__snippet").text if title_tag else ""
                        link = a_tag.get("href", "")

                        results.append({
                            "title": title.strip(),
                            "url": link.strip(),
                            "snippet": snippet.strip(),
                            "source": "Web Search"
                        })
            except Exception:
                pass

        return results
