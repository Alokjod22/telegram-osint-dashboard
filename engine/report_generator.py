import json
import os
from datetime import datetime

class ReportGenerator:
    """Generates structured investigation reports in Markdown, HTML, and JSON formats."""

    @staticmethod
    def generate_markdown_report(investigation_id: str, query: str, results: dict) -> str:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# OSINT RESEARCH REPORT

**Investigation ID**: `{investigation_id}`  
**Target Query**: `{query}`  
**Generated Date**: {now}  
**Methodology**: Open Source Intelligence (OSINT) Public Data Collection  

---

## 1. EXECUTIVE SUMMARY
Research conducted on query `{query}` across open public data sources.

## 2. FINDINGS & DATA DISCOVERY
```json
{json.dumps(results, indent=2)}
```

---

## 3. DISCLAIMER & CONFIDENCE
* All findings are derived from publicly accessible data sources.
* Confidence indicators are based on exact and near-exact public string matches.
"""
        return md

    @staticmethod
    def export_report_file(investigation_id: str, content: str, extension: str = "md") -> str:
        filename = f"report_{investigation_id}.{extension}"
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath
