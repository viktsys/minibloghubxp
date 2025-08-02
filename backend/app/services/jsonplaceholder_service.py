import requests
from typing import List, Optional


class JSONPlaceholderService:
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_posts(self) -> List[dict]:
        """Fetch all posts from JSONPlaceholder"""
        response = self.session.get(f"{self.BASE_URL}/posts")
        response.raise_for_status()
        return response.json()
    
    def get_post(self, post_id: int) -> Optional[dict]:
        """Fetch a specific post from JSONPlaceholder"""
        response = self.session.get(f"{self.BASE_URL}/posts/{post_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def get_comments(self, post_id: int) -> List[dict]:
        """Fetch comments for a specific post from JSONPlaceholder"""
        url = f"{self.BASE_URL}/posts/{post_id}/comments"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


jsonplaceholder_service = JSONPlaceholderService()
