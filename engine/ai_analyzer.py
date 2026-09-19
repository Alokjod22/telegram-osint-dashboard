import json
from google import genai
from config import settings

class AIAnalyzer:
    """AI Analysis engine using Gemini API for summarization, entity correlation, and report generation."""

    def __init__(self):
        self.client = None
        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception:
                self.client = None

    async def analyze_findings(self, query: str, raw_data: dict) -> dict:
        if not self.client:
            web_hits = len(raw_data.get("live_web_results", []))
            return {
                "ai_analysis": f"OSINT Investigation for target: {query}. Discovered {web_hits} live internet records. (Configure GEMINI_API_KEY for deep AI neural brief).",
                "summary": f"OSINT Investigation for target: {query}. Discovered {web_hits} live internet records.",
                "entities": [],
                "timeline": []
            }

        prompt = f"""
You are an expert OSINT Senior Threat Intelligence Analyst.
Analyze all collected public OSINT data and live internet search findings for query: '{query}'.

Target Data & Live Web Footprints:
{json.dumps(raw_data, indent=2)[:6000]}

Write a concise, professional OSINT Intelligence Brief in clear plain text / Markdown:
1. 👤 Target Identity & Associated Names: Mention any real names, aliases, corporate entities, or handles extracted from the web search snippets (or state if none indexed).
2. 🌐 Online Footprint & Indexed Pages: Summarize indexed pages, Truecaller entries, social media profile hints, or leak/paste occurrences.
3. 🛡️ Risk & Threat Assessment: Evaluate threat level (Low/Medium/High) based on exposure and carrier/location hints.
4. 💡 Key Takeaway / Investigation Next Step.
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            text_res = response.text.strip()
            return {
                "ai_analysis": text_res,
                "summary": text_res
            }
        except Exception as e:
            err_msg = f"AI analysis error: {str(e)}"
            return {"ai_analysis": err_msg, "summary": err_msg, "error": str(e)}
