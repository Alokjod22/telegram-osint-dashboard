import re
from typing import Dict, Any, List
from adapters.news_web_adapter import NewsWebAdapter

class PhoneAdapter:
    """Advanced OSINT adapter for phone number metadata, E.164 normalization, carrier estimation, risk scoring, multi-platform footprints, identity document dorks (Aadhaar/PAN), and live web OSINT indexing."""

    COUNTRY_CODES = {
        "91": {"country": "India 🇮🇳", "code": "IN", "region": "South Asia", "currency": "INR", "carrier_hint": "Jio / Airtel / Vi / BSNL"},
        "1": {"country": "United States / Canada 🇺🇸/🇨🇦", "code": "US/CA", "region": "North America", "currency": "USD/CAD", "carrier_hint": "Verizon / AT&T / T-Mobile"},
        "44": {"country": "United Kingdom 🇬🇧", "code": "GB", "region": "Europe", "currency": "GBP", "carrier_hint": "EE / Vodafone / O2 / Three"},
        "971": {"country": "United Arab Emirates 🇦🇪", "code": "AE", "region": "Middle East", "currency": "AED", "carrier_hint": "Etisalat / du"},
        "966": {"country": "Saudi Arabia 🇸🇦", "code": "SA", "region": "Middle East", "currency": "SAR", "carrier_hint": "STC / Mobily / Zain"},
        "92": {"country": "Pakistan 🇵🇰", "code": "PK", "region": "South Asia", "currency": "PKR", "carrier_hint": "Jazz / Telenor / Zong / Ufone"},
        "880": {"country": "Bangladesh 🇧🇩", "code": "BD", "region": "South Asia", "currency": "BDT", "carrier_hint": "Grameenphone / Robi / Banglalink"},
        "977": {"country": "Nepal 🇳🇵", "code": "NP", "region": "South Asia", "currency": "NPR", "carrier_hint": "Ncell / Nepal Telecom"},
        "94": {"country": "Sri Lanka 🇱🇰", "code": "LK", "region": "South Asia", "currency": "LKR", "carrier_hint": "Dialog / Mobitel"},
        "65": {"country": "Singapore 🇸🇬", "code": "SG", "region": "Southeast Asia", "currency": "SGD", "carrier_hint": "Singtel / StarHub / M1"},
        "60": {"country": "Malaysia 🇲🇾", "code": "MY", "region": "Southeast Asia", "currency": "MYR", "carrier_hint": "Maxis / CelcomDigi / U Mobile"},
        "49": {"country": "Germany 🇩🇪", "code": "DE", "region": "Europe", "currency": "EUR", "carrier_hint": "Telekom / Vodafone / O2"},
        "33": {"country": "France 🇫🇷", "code": "FR", "region": "Europe", "currency": "EUR", "carrier_hint": "Orange / SFR / Bouygues"},
        "61": {"country": "Australia 🇦🇺", "code": "AU", "region": "Oceania", "currency": "AUD", "carrier_hint": "Telstra / Optus / Vodafone"},
        "81": {"country": "Japan 🇯🇵", "code": "JP", "region": "East Asia", "currency": "JPY", "carrier_hint": "NTT Docomo / SoftBank / au"},
        "86": {"country": "China 🇨🇳", "code": "CN", "region": "East Asia", "currency": "CNY", "carrier_hint": "China Mobile / China Unicom / China Telecom"},
        "7": {"country": "Russia / Kazakhstan 🇷🇺/🇰🇿", "code": "RU/KZ", "region": "Eurasia", "currency": "RUB/KZT", "carrier_hint": "MTS / Beeline / MegaFon"}
    }

    @classmethod
    def analyze_phone(cls, phone_raw: str) -> Dict[str, Any]:
        # Normalize digits
        clean_digits = re.sub(r"[^\d+]", "", phone_raw)
        if not clean_digits.startswith("+"):
            clean_digits = "+" + clean_digits

        digits_only = clean_digits.lstrip("+")
        country_info = {
            "country": "International / Unknown 🌐",
            "code": "INTL",
            "region": "Global",
            "currency": "N/A",
            "carrier_hint": "Global Telecom Network"
        }

        # Match longest matching prefix
        matched_prefix = ""
        for prefix in sorted(cls.COUNTRY_CODES.keys(), key=lambda x: len(x), reverse=True):
            if digits_only.startswith(prefix):
                country_info = cls.COUNTRY_CODES[prefix]
                matched_prefix = prefix
                break

        # Line type heuristic
        line_type = "Mobile Line 📱"
        if len(digits_only) > 10 and (digits_only.endswith("00") or digits_only.startswith("1800") or digits_only.startswith("1888")):
            line_type = "Toll-Free / Corporate Business 🏢"
        elif len(digits_only) < 9:
            line_type = "Shortcode / Emergency / Internal ⚠️"

        valid_format = 7 <= len(digits_only) <= 15

        # Multi-Platform Footprint Links
        whatsapp_url = f"https://wa.me/{digits_only}"
        telegram_url = f"https://t.me/+{digits_only}"
        signal_url = f"https://signal.me/#p/{clean_digits}"
        truecaller_url = f"https://www.truecaller.com/search/{country_info['code'].lower()}/{digits_only}"
        
        twitter_url = f"https://twitter.com/search?q=%22{digits_only}%22+OR+%22{clean_digits}%22"
        facebook_url = f"https://www.facebook.com/search/top/?q={digits_only}"
        linkedin_url = f"https://www.google.com/search?q=site:linkedin.com/in/+%22{digits_only}%22+OR+%22{clean_digits}%22"
        instagram_url = f"https://www.google.com/search?q=site:instagram.com+%22{digits_only}%22+OR+%22{clean_digits}%22"
        skype_url = f"https://www.google.com/search?q=site:skype.com+%22{digits_only}%22"

        google_dork_url = f"https://www.google.com/search?q=%22{clean_digits}%22+OR+%22{digits_only}%22"
        social_dork_url = f"https://www.google.com/search?q=%22{digits_only}%22+site:facebook.com+OR+site:instagram.com+OR+site:twitter.com+OR+site:linkedin.com"
        breach_dork_url = f"https://www.google.com/search?q=%22{digits_only}%22+leak+OR+breach+OR+pastebin"

        # Government & Identity Card OSINT Dorks (Aadhaar / PAN / Voter / GSTIN)
        aadhaar_dork_url = f"https://www.google.com/search?q=%22{digits_only}%22+%22Aadhaar%22+OR+%22Adhar%22+OR+%22UIDAI%22+OR+%22XXXX%22"
        pan_dork_url = f"https://www.google.com/search?q=%22{digits_only}%22+%22PAN%22+OR+%22Income+Tax%22+OR+%22NSDL%22+OR+%22ITR%22"
        voter_dork_url = f"https://www.google.com/search?q=%22{digits_only}%22+%22Voter+ID%22+OR+%22EPIC%22+OR+%22Electoral%22"
        gstin_dork_url = f"https://www.google.com/search?q=%22{digits_only}%22+%22GSTIN%22+OR+%22UAN%22+OR+%22EPFO%22+OR+%22MSME%22"
        id_leak_dork_url = f"https://www.google.com/search?q=%22{digits_only}%22+filetype:pdf+OR+filetype:xlsx+OR+site:pastebin.com"

        # Risk scoring heuristic
        risk_score = "LOW"
        risk_factors = []
        if not valid_format:
            risk_score = "HIGH"
            risk_factors.append("Non-standard digits length")
        if line_type.startswith("Toll-Free"):
            risk_factors.append("Shared corporate line")
        if matched_prefix == "":
            risk_factors.append("Unrecognized international country prefix")

        return {
            "input_phone": phone_raw,
            "normalized_e164": clean_digits,
            "digits_only": digits_only,
            "country": country_info["country"],
            "country_code": country_info["code"],
            "region": country_info["region"],
            "carrier_hint": country_info["carrier_hint"],
            "line_type": line_type,
            "valid_format": valid_format,
            "risk_score": risk_score,
            "risk_factors": risk_factors if risk_factors else ["Clean format"],
            "whatsapp_url": whatsapp_url,
            "telegram_url": telegram_url,
            "signal_url": signal_url,
            "truecaller_url": truecaller_url,
            "twitter_url": twitter_url,
            "facebook_url": facebook_url,
            "linkedin_url": linkedin_url,
            "instagram_url": instagram_url,
            "skype_url": skype_url,
            "google_dork_url": google_dork_url,
            "social_dork_url": social_dork_url,
            "breach_dork_url": breach_dork_url,
            "aadhaar_dork_url": aadhaar_dork_url,
            "pan_dork_url": pan_dork_url,
            "voter_dork_url": voter_dork_url,
            "gstin_dork_url": gstin_dork_url,
            "id_leak_dork_url": id_leak_dork_url,
            "live_web_results": [],
            "extracted_id_cards": []
        }

    @classmethod
    async def analyze_phone_async(cls, phone_raw: str) -> Dict[str, Any]:
        data = cls.analyze_phone(phone_raw)
        digits_only = data["digits_only"]
        clean_digits = data["normalized_e164"]

        # Run live web OSINT search across the internet
        query_str = f"{digits_only}"
        web_results = await NewsWebAdapter.search_web(query_str, max_results=5)
        
        # Also run secondary search for identity card & document footprints
        id_query_str = f"{digits_only} Aadhaar OR PAN OR Voter OR GST"
        id_results = await NewsWebAdapter.search_web(id_query_str, max_results=3)

        # Combine & deduplicate live web findings
        combined_results = list({r["url"]: r for r in (web_results + id_results)}.values())
        
        # Scan snippets for PAN and Aadhaar patterns
        extracted_ids = []
        pan_pattern = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b")
        aadhaar_pattern = re.compile(r"\b[2-9]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}\b|\bXXXX[\s\-]?XXXX[\s\-]?\d{4}\b", re.IGNORECASE)

        for res_item in combined_results:
            text_to_scan = f"{res_item.get('title', '')} {res_item.get('snippet', '')}"
            pan_matches = pan_pattern.findall(text_to_scan)
            aadhaar_matches = aadhaar_pattern.findall(text_to_scan)
            for p in pan_matches:
                extracted_ids.append(f"PAN: {p}")
            for a in aadhaar_matches:
                extracted_ids.append(f"Aadhaar: {a}")

        data["live_web_results"] = combined_results[:6]
        data["extracted_id_cards"] = list(set(extracted_ids))
        return data
