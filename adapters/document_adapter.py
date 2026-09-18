import json
import re
from typing import Dict, Any, List

class DocumentAdapter:
    """OSINT adapter for extracting text, URLs, emails, and entities from uploaded documents (TXT, JSON, CSV, PDF)."""

    @staticmethod
    def parse_text_content(content: str) -> Dict[str, Any]:
        # Regex entity extractors
        urls = re.findall(r"https?://[^\s<>\"']+", content)
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content)
        ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", content)
        domains = re.findall(r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", content)

        return {
            "char_count": len(content),
            "line_count": len(content.splitlines()),
            "extracted_urls": list(set(urls)),
            "extracted_emails": list(set(emails)),
            "extracted_ips": list(set(ips)),
            "extracted_domains": list(set(domains) - set(emails)),
            "sample_text": content[:500]
        }
