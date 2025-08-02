import requests
from typing import Optional, Dict, Any
from app.core.config import settings


class UnsplashService:
    BASE_URL = "https://api.unsplash.com"
    
    def __init__(self):
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup authentication headers based on available credentials"""
        if not settings.UNSPLASH_ACCESS_KEY:
            return
            
        # For most operations, we use Client-ID authentication
        self.session.headers.update({
            "Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"
        })
        
        # Store secret key for operations that might need it
        self._secret_key = settings.UNSPLASH_SECRET_KEY
    
    def _get_authenticated_session(self, use_secret: bool = False):
        """Get session with appropriate authentication"""
        if not settings.UNSPLASH_ACCESS_KEY:
            raise ValueError("Unsplash Access Key not configured")
            
        session = requests.Session()
        
        if use_secret and settings.UNSPLASH_SECRET_KEY:
            # For operations requiring secret key, we would typically
            # implement OAuth flow, but for server-to-server operations
            # we can use the secret key directly in some cases
            session.headers.update({
                "Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}",
                "X-Unsplash-Client": f"secret:{settings.UNSPLASH_SECRET_KEY}"
            })
        else:
            # Standard Client-ID authentication
            session.headers.update({
                "Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"
            })
            
        return session
    
    def _validate_credentials(self) -> bool:
        """Validate that credentials are properly configured"""
        if not settings.UNSPLASH_ACCESS_KEY:
            return False
            
        # Test the credentials by making a simple API call
        try:
            response = self.session.get(
                f"{self.BASE_URL}/photos",
                params={"per_page": 1}
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def search_photos(
        self,
        query: str,
        per_page: int = 10,
        page: int = 1
    ) -> Dict[str, Any]:
        """Search for photos on Unsplash"""
        if not settings.UNSPLASH_ACCESS_KEY:
            return {"results": [], "total": 0, "total_pages": 0}
        
        # Validate credentials before making request
        if not self._validate_credentials():
            raise ValueError("Invalid Unsplash credentials")
        
        params = {
            "query": query,
            "per_page": min(per_page, 30),  # Unsplash max is 30
            "page": page,
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/search/photos",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Unauthorized: Check your Unsplash credentials"
                )
            elif e.response.status_code == 403:
                raise ValueError(
                    "Forbidden: API rate limit exceeded or invalid key"
                )
            else:
                raise ValueError(
                    f"Unsplash API error: {e.response.status_code}"
                )
    
    def get_photo(self, photo_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific photo"""
        if not settings.UNSPLASH_ACCESS_KEY:
            return None
        
        if not self._validate_credentials():
            raise ValueError("Invalid Unsplash credentials")
            
        try:
            response = self.session.get(f"{self.BASE_URL}/photos/{photo_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Unauthorized: Check your Unsplash credentials"
                )
            else:
                raise ValueError(
                    f"Unsplash API error: {e.response.status_code}"
                )
    
    def trigger_download(self, download_url: str) -> bool:
        """
        Trigger a download event (required by Unsplash API)
        This helps track photo usage for attribution
        """
        if not settings.UNSPLASH_ACCESS_KEY or not download_url:
            return False
        
        try:
            # Use authenticated session for download tracking
            session = self._get_authenticated_session()
            response = session.get(download_url)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_user_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get current user's API usage statistics
        Requires both access key and secret key for enhanced access
        """
        if (not settings.UNSPLASH_ACCESS_KEY or
                not settings.UNSPLASH_SECRET_KEY):
            return None
        
        try:
            # Use secret key for enhanced operations
            session = self._get_authenticated_session(use_secret=True)
            response = session.get(f"{self.BASE_URL}/me")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def get_api_limits(self) -> Dict[str, Any]:
        """Get current API rate limits and usage"""
        try:
            # Make a minimal request to check headers
            response = self.session.get(
                f"{self.BASE_URL}/photos",
                params={"per_page": 1}
            )
            
            return {
                "rate_limit": response.headers.get("X-Ratelimit-Limit"),
                "remaining": response.headers.get("X-Ratelimit-Remaining"),
                "reset_time": response.headers.get("X-Ratelimit-Reset"),
                "status_code": response.status_code
            }
        except Exception:
            return {
                "rate_limit": None,
                "remaining": None,
                "reset_time": None,
                "status_code": None
            }


unsplash_service = UnsplashService()
