import uuid
from typing import Dict, Any
from adapters.domain_adapter import DomainAdapter
from adapters.username_adapter import UsernameAdapter
from adapters.phone_adapter import PhoneAdapter
from adapters.news_web_adapter import NewsWebAdapter
from engine.ai_analyzer import AIAnalyzer
from engine.report_generator import ReportGenerator

class ResearchManager:
    """Core coordinator for executing OSINT investigations across domain, username, phone, and news adapters."""

    def __init__(self):
        self.ai_analyzer = AIAnalyzer()

    async def execute_investigation(self, query: str, search_type: str = "AUTO") -> Dict[str, Any]:
        inv_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        query_clean = query.strip()

        # Determine type if AUTO
        if search_type == "AUTO":
            if "." in query_clean and not "@" in query_clean and not " " in query_clean:
                search_type = "DOMAIN"
            elif query_clean.startswith("+") or query_clean.isdigit():
                search_type = "PHONE"
            elif query_clean.startswith("@"):
                search_type = "USERNAME"
            else:
                search_type = "WEB"

        results = {
            "investigation_id": inv_id,
            "query": query_clean,
            "search_type": search_type,
            "data": {}
        }

        if search_type == "DOMAIN":
            results["data"] = await DomainAdapter.analyze_domain(query_clean)
        elif search_type == "USERNAME":
            results["data"] = await UsernameAdapter.search_username(query_clean)
        elif search_type == "PHONE":
            results["data"] = PhoneAdapter.analyze_phone(query_clean)
        else:
            results["data"] = {"web_results": await NewsWebAdapter.search_web(query_clean)}

        # Perform AI analysis
        ai_res = await self.ai_analyzer.analyze_findings(query_clean, results["data"])
        results["ai_analysis"] = ai_res

        # Generate report
        report_md = ReportGenerator.generate_markdown_report(inv_id, query_clean, results)
        results["report_markdown"] = report_md

        return results
