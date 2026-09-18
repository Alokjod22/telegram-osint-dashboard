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
            return {
                "summary": f"OSINT Investigation results for: {query}. (Gemini API key not configured for AI analysis)",
                "entities": [],
                "timeline": []
            }

        prompt = f"""
You are an expert OSINT Intelligence Analyst.
Analyze the following public OSINT data for query: '{query}'.

Data:
{json.dumps(raw_data, indent=2)[:4000]}

Provide a JSON response with:
1. "summary": A concise executive summary of key findings.
2. "entities": A list of extracted entities (person, organization, domain, location).
3. "timeline": Key dates or events discovered.
4. "confidence_score": Confidence score from 0.0 to 1.0 based on public evidence.
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return {"ai_analysis": response.text}
        except Exception as e:
            return {"error": f"AI analysis error: {str(e)}", "summary": "Failed to generate AI analysis."}
