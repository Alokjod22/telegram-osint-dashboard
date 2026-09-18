import re
from typing import Dict, Any

class PhoneAdapter:
    """OSINT adapter for phone number metadata, E.164 normalization, and country/carrier detection."""

    COUNTRY_CODES = {
        "1": {"country": "United States / Canada", "code": "US/CA"},
        "44": {"country": "United Kingdom", "code": "GB"},
        "91": {"country": "India", "code": "IN"},
        "49": {"country": "Germany", "code": "DE"},
        "33": {"country": "France", "code": "FR"},
        "61": {"country": "Australia", "code": "AU"},
        "81": {"country": "Japan", "code": "JP"},
        "86": {"country": "China", "code": "CN"},
        "7": {"country": "Russia / Kazakhstan", "code": "RU/KZ"}
    }

    @classmethod
    def analyze_phone(cls, phone_raw: str) -> Dict[str, Any]:
        # Normalize digits
        clean_digits = re.sub(r"[^\d+]", "", phone_raw)
        if not clean_digits.startswith("+"):
            clean_digits = "+" + clean_digits

        country_info = {"country": "Unknown / International", "code": "INTL"}
        digits_only = clean_digits.lstrip("+")

        for prefix, info in cls.COUNTRY_CODES.items():
            if digits_only.startswith(prefix):
                country_info = info
                break

        # Line type heuristic
        line_type = "Mobile / Fixed Line"
        if len(digits_only) > 10 and digits_only.endswith("00"):
            line_type = "Toll Free / Business"

        return {
            "input_phone": phone_raw,
            "normalized_e164": clean_digits,
            "country": country_info["country"],
            "country_code": country_info["code"],
            "line_type": line_type,
            "valid_format": len(digits_only) >= 7 and len(digits_only) <= 15
        }
