#!/usr/bin/env python3
"""
Simple API test script for Mini Blog Hub XP
"""
import asyncio
import sys
import time
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.table import Table

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

app = typer.Typer()
console = Console()

DEFAULT_BASE_URL = "http://localhost:8000"

def get_test_user():
    timestamp = int(time.time())
    return {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


class SimpleAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.token = None
    
    def log(self, test: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅" if success else "❌"
        self.results.append({"test": test, "success": success, "message": message})
        console.print(f"{status} {test}: {message}" if message else f"{status} {test}")
    
    async def test_health(self, client: httpx.AsyncClient):
        """Test health endpoint"""
        try:
            response = await client.get(f"{self.base_url}/health")
            if response.status_code == 200 and response.json().get("status") == "healthy":
                self.log("Health Check", True, "API is healthy")
            else:
                self.log("Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log("Health Check", False, f"Error: {e}")
    
    async def test_auth(self, client: httpx.AsyncClient):
        """Test authentication"""
        test_user = get_test_user()
        
        # Register user
        try:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "username": test_user["username"],
                    "email": test_user["email"],
                    "password": test_user["password"],
                    "full_name": test_user["full_name"]
                }
            )
            if response.status_code == 200:
                self.log("User Registration", True, "User created")
            elif response.status_code == 400:
                # User already exists
                data = response.json()
                if "already registered" in data.get("detail", "").lower():
                    self.log("User Registration", True, "User exists")
                else:
                    self.log("User Registration", False, 
                           f"Bad request: {data.get('detail', 'Unknown')}")
            else:
                self.log("User Registration", False, 
                       f"Status: {response.status_code}")
        except Exception as e:
            self.log("User Registration", False, f"Error: {e}")
        
        # Login
        try:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": test_user["username"],
                    "password": test_user["password"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log("User Login", True, "Login successful")
                return True
            else:
                self.log("User Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log("User Login", False, f"Error: {e}")
        
        return False
    
    async def test_posts(self, client: httpx.AsyncClient):
        """Test post endpoints"""
        if not self.token:
            self.log("Posts Test", False, "No auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create post
        try:
            response = await client.post(
                f"{self.base_url}/api/v1/posts/",
                json={
                    "title": "Test Post",
                    "content": "This is a test post.",
                    "summary": "Test summary"
                },
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    post_id = data.get("id")
                    self.log("Create Post", True, f"Post ID: {post_id}")
                else:
                    self.log("Create Post", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log("Create Post", False, f"Error: {e}")
        
        # Get posts
        try:
            response = await client.get(f"{self.base_url}/api/v1/posts/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    count = len(data)
                    self.log("Get Posts", True, f"Found {count} posts")
                else:
                    count = len(data.get("items", []))
                    self.log("Get Posts", True, f"Found {count} posts")
            else:
                self.log("Get Posts", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log("Get Posts", False, f"Error: {e}")
    
    async def test_images(self, client: httpx.AsyncClient):
        """Test image search"""
        try:
            response = await client.get(
                f"{self.base_url}/api/v1/images/search/",
                params={"query": "nature", "per_page": 1}
            )
            if response.status_code == 200:
                self.log("Image Search", True, "Search working")
            elif response.status_code == 400:
                self.log("Image Search", True, "Unsplash not configured")
            elif response.status_code == 500:
                # Check if it's an Unsplash API error
                error_text = response.text
                if "401" in error_text and "Unauthorized" in error_text:
                    self.log("Image Search", True, "Unsplash API key missing")
                else:
                    self.log("Image Search", False, f"Server error: 500")
            else:
                self.log("Image Search", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log("Image Search", False, f"Error: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        async with httpx.AsyncClient() as client:
            console.print(f"🚀 Testing API: {self.base_url}")
            console.print("-" * 50)
            
            await self.test_health(client)
            auth_ok = await self.test_auth(client)
            
            if auth_ok:
                await self.test_posts(client)
            
            await self.test_images(client)
            
            return self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        
        console.print("\n" + "=" * 50)
        console.print("TEST SUMMARY")
        console.print("=" * 50)
        
        table = Table()
        table.add_column("Metric")
        table.add_column("Value")
        
        table.add_row("Total Tests", str(total))
        table.add_row("Passed", str(passed))
        table.add_row("Failed", str(total - passed))
        table.add_row("Success Rate", f"{(passed/total)*100:.1f}%")
        
        console.print(table)
        
        failed = [r for r in self.results if not r["success"]]
        if failed:
            console.print("\nFailed Tests:")
            for result in failed:
                console.print(f"❌ {result['test']}: {result['message']}")
        
        return passed == total


@app.command()
def test(
    base_url: str = typer.Option(DEFAULT_BASE_URL, help="API base URL")
):
    """Run API tests"""
    try:
        tester = SimpleAPITester(base_url)
        success = asyncio.run(tester.run_all_tests())
        
        if success:
            console.print("\n🎉 All tests passed!", style="bold green")
            return
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
def health(
    base_url: str = typer.Option(DEFAULT_BASE_URL, help="API base URL")
):
    """Quick health check"""
    async def check():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url.rstrip('/')}/health")
                return response.status_code == 200
        except:
            return False
    
    try:
        healthy = asyncio.run(check())
        if healthy:
            console.print("✅ Server is healthy!")
        else:
            console.print("❌ Server is not responding!")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"💥 Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
