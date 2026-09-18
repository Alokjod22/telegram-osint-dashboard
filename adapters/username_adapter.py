import httpx
from typing import Dict, Any, List

class UsernameAdapter:
    """OSINT adapter for public platform username intelligence."""

    PLATFORMS = {
        "GitHub": "https://github.com/{}",
        "GitLab": "https://gitlab.com/{}",
        "Twitter/X": "https://x.com/{}",
        "Reddit": "https://www.reddit.com/user/{}",
        "Dev.to": "https://dev.to/{}",
        "Medium": "https://medium.com/@{}",
        "DockerHub": "https://hub.docker.com/u/{}"
    }

    @classmethod
    async def search_username(cls, username: str) -> Dict[str, Any]:
        username = username.strip().lstrip("@")
        results = {
            "username": username,
            "profiles": [],
            "total_matches": 0
        }

        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            for platform, url_template in cls.PLATFORMS.items():
                profile_url = url_template.format(username)
                try:
                    resp = await client.get(profile_url)
                    if resp.status_code == 200:
                        results["profiles"].append({
                            "platform": platform,
                            "profile_url": profile_url,
                            "status": "EXISTS",
                            "confidence": 0.95
                        })
                except Exception:
                    pass

        results["total_matches"] = len(results["profiles"])
        return results
