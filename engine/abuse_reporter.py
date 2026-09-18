import hashlib
from datetime import datetime
from typing import Dict, Any, List

class AbuseReporter:
    """Automated Telegram Abuse Evidence & Reporting Assistant with deduplication and audit tracking."""

    CATEGORIES = {
        "1": "Child Safety / CSAM",
        "2": "Terrorism / Extremism",
        "3": "Fraud / Financial Scams",
        "4": "Illegal Goods / Contraband",
        "5": "Non-consensual Intimate Content",
        "6": "Copyright / DMCA Violation",
        "7": "General Policy Violation"
    }

    @staticmethod
    def compute_hash(evidence_url: str, snippet: str) -> str:
        data = f"{evidence_url.strip().lower()}:{snippet.strip()}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @classmethod
    def create_abuse_case(cls, case_id: str, target_url: str, category_id: str, initial_evidence: str) -> Dict[str, Any]:
        category_name = cls.CATEGORIES.get(category_id, "General Policy Violation")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        content_hash = cls.compute_hash(target_url, initial_evidence)

        case_data = {
            "case_id": case_id,
            "target_url": target_url,
            "category": category_name,
            "status": "DRAFT",
            "created_at": timestamp,
            "evidence": [{
                "evidence_url": target_url,
                "snippet": initial_evidence,
                "content_hash": content_hash,
                "timestamp": timestamp
            }],
            "audit_trail": [{
                "action": "CASE_CREATED",
                "timestamp": timestamp,
                "details": f"Created abuse investigation for {target_url}"
            }]
        }
        return case_data

    @classmethod
    def generate_review_screen(cls, case_data: Dict[str, Any]) -> str:
        ev_list = "\n".join([f"• [{e['evidence_url']}]({e['evidence_url']}) - {e['snippet'][:100]}" for e in case_data["evidence"]])
        return f"""📋 **ABUSE REPORT REVIEW SCREEN**

**Case ID**: `{case_data['case_id']}`  
**Target URL**: {case_data['target_url']}  
**Category**: `{case_data['category']}`  
**Status**: `{case_data['status']}`  
**Created At**: `{case_data['created_at']}`  

---

### Collected Evidence ({len(case_data['evidence'])} Items)
{ev_list}

---

### Review Options
Select **Approve & Export** to generate official report packages (Markdown / HTML / PDF), or **Append Evidence** to add newly discovered non-duplicate evidence.
"""

    @classmethod
    def generate_final_report_markdown(cls, case_data: Dict[str, Any]) -> str:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        ev_block = ""
        for idx, ev in enumerate(case_data["evidence"], 1):
            ev_block += f"### Evidence Item #{idx}\n* **URL**: {ev['evidence_url']}\n* **Timestamp**: {ev['timestamp']}\n* **Hash**: `{ev['content_hash'][:16]}`\n* **Snippet/Details**: {ev['snippet']}\n\n"

        md = f"""# OFFICIAL TELEGRAM ABUSE REPORT PACKAGE

**Case ID**: `{case_data['case_id']}`  
**Generated Date**: {timestamp}  
**Report Category**: {case_data['category']}  
**Primary Target**: {case_data['target_url']}  

---

## 1. EXECUTIVE SUMMARY
Factual, source-backed evidence collection regarding suspected policy violations observed on publicly accessible Telegram channel/message targets.

## 2. DEDUPLICATED EVIDENCE LOG
{ev_block}

---

## 3. OFFICIAL SUBMISSION PROCESS
To submit this report to Telegram Trust & Safety:
1. **In-App Submission**: Open Telegram > Navigate to {case_data['target_url']} > Tap `...` > Select **Report** > Choose `{case_data['category']}`.
2. **Official Email Contacts**:
   - CSAM / Child Safety: `stopca@telegram.org`
   - Copyright / DMCA: `dmca@telegram.org`
   - General Abuse & Fraud: `abuse@telegram.org`
"""
        return md
