import pytest
import asyncio
from adapters.phone_adapter import PhoneAdapter
from adapters.document_adapter import DocumentAdapter
from engine.abuse_reporter import AbuseReporter
from engine.report_generator import ReportGenerator

def test_phone_adapter():
    res = PhoneAdapter.analyze_phone("+14155552671")
    assert res["normalized_e164"] == "+14155552671"
    assert res["country_code"] == "US/CA"
    assert res["valid_format"] is True

def test_document_adapter():
    sample_text = "Contact support at info@example.com or visit https://example.com/status from 192.168.1.1."
    parsed = DocumentAdapter.parse_text_content(sample_text)
    assert "info@example.com" in parsed["extracted_emails"]
    assert "https://example.com/status" in parsed["extracted_urls"]
    assert "192.168.1.1" in parsed["extracted_ips"]

def test_abuse_reporter():
    case = AbuseReporter.create_abuse_case("CASE-101", "https://t.me/sample_channel", "3", "Financial scam details")
    assert case["category"] == "Fraud / Financial Scams"
    assert case["status"] == "DRAFT"
    assert len(case["evidence"]) == 1
    assert case["evidence"][0]["content_hash"] is not None

def test_report_generator():
    md = ReportGenerator.generate_markdown_report("INV-12345", "example.com", {"status": "ok"})
    assert "INV-12345" in md
    assert "example.com" in md
