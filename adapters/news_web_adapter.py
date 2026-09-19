import httpx
import re
from typing import Dict, Any, List

class NewsWebAdapter:
    """OSINT adapter for searching news articles, web content, and indexing phone numbers/entities across the live internet."""

    @staticmethod
    async def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results = []
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://html.duckduckgo.com",
            "Referer": "https://html.duckduckgo.com/"
        }
        data = {"q": query, "b": "", "kl": "us-en"}

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                resp = await client.post(url, headers=headers, data=data)
                if resp.status_code == 200:
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(resp.text, "html.parser")
                        for body in soup.find_all("div", class_="result__body", limit=max_results):
                            title_a = body.find("a", class_="result__a")
                            snippet_a = body.find("a", class_="result__snippet")
                            url_a = body.find("a", class_="result__url")
                            if title_a:
                                title = title_a.get_text(strip=True)
                                snippet = snippet_a.get_text(strip=True) if snippet_a else ""
                                link = url_a.get("href", "").strip() if url_a else title_a.get("href", "").strip()
                                results.append({
                                    "title": title,
                                    "snippet": snippet,
                                    "url": link,
                                    "source": "Web Search"
                                })
                    except Exception:
                        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
                        snippets = re.findall(r'class="result__snippet[^"]*"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
                        urls = re.findall(r'class="result__url"[^>]*href="([^"]+)"', resp.text)
                        for i in range(min(len(titles), max_results)):
                            clean_title = re.sub(r'<[^>]+>', '', titles[i]).strip()
                            clean_snip = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""
                            clean_url = urls[i].strip() if i < len(urls) else ""
                            results.append({
                                "title": clean_title,
                                "snippet": clean_snip,
                                "url": clean_url,
                                "source": "Web Search"
                            })
            except Exception:
                pass

        return results
