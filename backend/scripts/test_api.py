#!/usr/bin/env python3
"""
Comprehensive test script for Mini Blog Hub XP API
"""
import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import httpx
import typer
from rich.console import Console
from rich.table import Table

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

app = typer.Typer()
console = Console()

# Test configuration
DEFAULT_BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"


class APITester:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient()
        self.access_token: Optional[str] = None
        self.test_results = []
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test(
        self, 
        test_name: str, 
        success: bool, 
        message: str = "", 
        response_time: float = 0
    ):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_time": response_time
        })
        
        time_info = f" ({response_time:.2f}s)" if response_time > 0 else ""
        if message:
            console.print(f"{status} {test_name}{time_info}: {message}")
        else:
            console.print(f"{status} {test_name}{time_info}")
    
    async def test_health_check(self):
        """Test basic health endpoints"""
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.base_url}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, 
                                "API is healthy", response_time)
                else:
                    self.log_test("Health Check", False, 
                                f"Unexpected response: {data}")
            else:
                self.log_test("Health Check", False, 
                            f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
    
    async def test_user_registration(
        self, 
        email: str, 
        password: str, 
        full_name: str = "Test User"
    ):
        """Test user registration"""
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "full_name": full_name
                }
            )
            response_time = time.time() - start_time
            
            if response.status_code == 201:
                data = response.json()
                if "id" in data and "email" in data:
                    self.log_test("User Registration", True, 
                                f"User created: {email}", response_time)
                    return True
            elif response.status_code == 400:
                data = response.json()
                if "already registered" in data.get("detail", "").lower():
                    self.log_test("User Registration", True, 
                                f"User exists: {email}", response_time)
                    return True
            
            self.log_test("User Registration", False, 
                        f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            return False
    
    async def test_user_login(self, email: str, password: str) -> bool:
        """Test user login and store access token"""
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": email,
                    "password": password
                }
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.log_test("User Login", True, 
                                f"Logged in: {email}", response_time)
                    return True
            
            self.log_test("User Login", False, 
                        f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def test_create_post(self) -> Optional[int]:
        """Test creating a post"""
        if not self.access_token:
            self.log_test("Create Post", False, "No access token")
            return None
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/v1/posts/",
                json={
                    "title": "Test Post",
                    "content": "Test post content from API test script.",
                    "summary": "Test post summary"
                },
                headers=self.get_auth_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 201:
                data = response.json()
                if "id" in data:
                    post_id = data["id"]
                    self.log_test("Create Post", True, 
                                f"Post created: {post_id}", response_time)
                    return post_id
            
            self.log_test("Create Post", False, 
                        f"Status: {response.status_code}")
            return None
        except Exception as e:
            self.log_test("Create Post", False, f"Error: {str(e)}")
            return None
    
    async def test_get_posts(self):
        """Test getting posts list"""
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.base_url}/api/v1/posts/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    count = len(data["items"])
                    self.log_test("Get Posts", True, 
                                f"Retrieved {count} posts", response_time)
                    return
            
            self.log_test("Get Posts", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Posts", False, f"Error: {str(e)}")
    
    async def test_search_images(self):
        """Test image search functionality"""
        try:
            start_time = time.time()
            response = await self.client.get(
                f"{self.base_url}/api/v1/images/search/",
                params={"query": "nature", "per_page": 5}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "images" in data:
                    count = len(data["images"])
                    self.log_test("Search Images", True, 
                                f"Found {count} images", response_time)
                    return
            elif response.status_code == 400:
                data = response.json()
                if "unsplash" in data.get("detail", "").lower():
                    self.log_test("Search Images", True, 
                                "Unsplash not configured", response_time)
                    return
            
            self.log_test("Search Images", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Search Images", False, f"Error: {str(e)}")
    
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        try:
            start_time = time.time()
            
            # Make rapid requests to trigger rate limiting
            for i in range(70):
                response = await self.client.get(f"{self.base_url}/health")
                if response.status_code == 429:
                    response_time = time.time() - start_time
                    self.log_test("Rate Limiting", True, 
                                "Rate limiting works", response_time)
                    return
            
            self.log_test("Rate Limiting", False, "Not triggered")
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        console.print("\n" + "="*60)
        console.print("TEST SUMMARY", style="bold blue")
        console.print("="*60)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Tests", str(total))
        table.add_row("Passed", str(passed))
        table.add_row("Failed", str(failed))
        table.add_row("Success Rate", f"{(passed/total)*100:.1f}%")
        
        console.print(table)
        
        if failed > 0:
            console.print("\nFAILED TESTS:", style="bold red")
            for result in self.test_results:
                if not result["success"]:
                    console.print(f"❌ {result['test']}: {result['message']}")
        
        console.print("\n" + "="*60)
        return failed == 0


async def run_comprehensive_test(base_url: str):
    """Run all API tests"""
    async with APITester(base_url) as tester:
        console.print(f"🚀 Testing API: {base_url}", style="bold green")
        console.print("="*60)
        
        # Basic health checks
        await tester.test_health_check()
        
        # Authentication tests
        await tester.test_user_registration(
            TEST_USER_EMAIL, TEST_USER_PASSWORD, "Test User"
        )
        login_success = await tester.test_user_login(
            TEST_USER_EMAIL, TEST_USER_PASSWORD
        )
        
        if login_success:
            # Content tests
            post_id = await tester.test_create_post()
            await tester.test_get_posts()
            
            # External API tests
            await tester.test_search_images()
        
        # Rate limiting test
        await tester.test_rate_limiting()
        
        return tester.print_summary()


@app.command()
def run_tests(
    base_url: str = typer.Option(DEFAULT_BASE_URL, help="API base URL"),
):
    """Run comprehensive API tests"""
    try:
        success = asyncio.run(run_comprehensive_test(base_url))
        if success:
            console.print("\n🎉 All tests passed!", style="bold green")
            raise typer.Exit(0)
        else:
            console.print("\n💥 Some tests failed!", style="bold red")
            raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n⚠️ Tests interrupted", style="yellow")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n💥 Error: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def health_check(
    base_url: str = typer.Option(DEFAULT_BASE_URL, help="API base URL")
):
    """Quick server health check"""
    async def quick_check():
        async with APITester(base_url) as tester:
            await tester.test_health_check()
            return all(r["success"] for r in tester.test_results)
    
    try:
        healthy = asyncio.run(quick_check())
        if healthy:
            console.print("✅ Server is healthy!", style="bold green")
            raise typer.Exit(0)
        else:
            console.print("❌ Server health check failed!", style="bold red")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"💥 Error: {e}", style="bold red")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
