import httpx
import dns.resolver
from typing import Dict, Any, List

class DomainAdapter:
    """OSINT adapter for public Domain, DNS, RDAP, HTTP security, and website intelligence."""

    @staticmethod
    async def analyze_domain(domain: str) -> Dict[str, Any]:
        domain = domain.lower().replace("http://", "").replace("https://", "").strip("/")
        results = {
            "domain": domain,
            "dns_records": {},
            "rdap": {},
            "http_headers": {},
            "robots_txt": None,
            "security_score": 0,
            "subdomains": []
        }

        # 1. DNS Records Lookup
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                results["dns_records"][rtype] = [str(rdata) for rdata in answers]
            except Exception:
                results["dns_records"][rtype] = []

        # 2. HTTP Headers & Security Audit
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                resp = await client.get(f"https://{domain}")
                results["http_headers"] = dict(resp.headers)

                # Check security headers
                sec_headers = ["strict-transport-security", "content-security-policy", "x-frame-options", "x-content-type-options"]
                present_sec = [h for h in sec_headers if h in resp.headers]
                results["security_score"] = len(present_sec) * 25

            except Exception as e:
                results["http_headers_error"] = str(e)

            # 3. Robots.txt Inspection
            try:
                robots_resp = await client.get(f"https://{domain}/robots.txt")
                if robots_resp.status_code == 200:
                    results["robots_txt"] = robots_resp.text[:1000] # Limit snippet size
            except Exception:
                results["robots_txt"] = None

        # 4. Public RDAP Info
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                rdap_resp = await client.get(f"https://rdap.org/domain/{domain}")
                if rdap_resp.status_code == 200:
                    rdap_data = rdap_resp.json()
                    results["rdap"] = {
                        "handle": rdap_data.get("handle"),
                        "registrar": rdap_data.get("port43"),
                        "status": rdap_data.get("status", [])
                    }
            except Exception:
                results["rdap"] = {}

        return results
