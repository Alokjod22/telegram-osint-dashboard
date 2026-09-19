import json
from google import genai
from config import settings

class AIAnalyzer:
    """AI Analysis engine using Gemini API with automatic model failover fallback for summarization, entity correlation, and report generation."""

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
You are an expert OSINT Senior Threat Intelligence & Identity Analyst.
Analyze all collected public OSINT data, live web search findings, and identity card footprints for query: '{query}'.

Target Data & Live Web Footprints:
{json.dumps(raw_data, indent=2)[:6500]}

Write a concise, professional OSINT Intelligence Brief in clear plain text / Markdown:
1. 👤 Target Identity & Associated Names: Mention any real names, aliases, corporate entities, or handles extracted from web search snippets (or state if none indexed).
2. 🪪 Aadhaar / PAN / Identity Document Findings: State whether any Aadhaar numbers, PAN cards, Voter ID records, or tax registrations are indexed or linked to this number.
3. 🌐 Online Footprint & Indexed Pages: Summarize indexed web pages, Truecaller listings, social media profile hints, or leak/paste occurrences.
4. 🛡️ Risk & Threat Assessment: Evaluate threat level (Low/Medium/High) based on exposure and carrier/location hints.
5. 💡 Actionable Next Step for Investigator.
"""

        models_to_try = [
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-2.5-flash',
            'gemini-2.5-pro'
        ]

        last_error = ""
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                text_res = response.text.strip()
                if text_res:
                    return {
                        "ai_analysis": text_res,
                        "summary": text_res
                    }
            except Exception as e:
                last_error = str(e)
                continue

        err_msg = f"AI Analysis Service Notice: {last_error}"
        return {"ai_analysis": err_msg, "summary": err_msg, "error": last_error}
