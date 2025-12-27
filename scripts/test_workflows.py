"""
Manual testing script for Cinema Booking System workflows.
Run this to test your API endpoints interactively.
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


class Colors:
    """ANSI color codes for pretty output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class CinemaAPITester:
    """Test helper for Cinema Booking System"""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.session = requests.Session()
        
    def log_success(self, message: str):
        """Log successful operation"""
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")
    
    def log_error(self, message: str):
        """Log failed operation"""
        print(f"{Colors.RED}✗ {message}{Colors.RESET}")
    
    def log_info(self, message: str):
        """Log informational message"""
        print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")
    
    def log_section(self, message: str):
        """Log section header"""
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"{message}")
        print(f"{'='*60}{Colors.RESET}\n")
    
    def pretty_print_response(self, response: requests.Response):
        """Pretty print API response"""
        print(f"Status: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
        print()
    
    def register_user(self, email: str, password: str) -> bool:
        """Register a new user"""
        self.log_info(f"Registering user: {email}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/register",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 201:
                data = response.json()
                self.log_success(f"User registered successfully")
                self.pretty_print_response(response)
                return True
            else:
                self.log_error(f"Registration failed: {response.status_code}")
                self.pretty_print_response(response)
                return False
                
        except Exception as e:
            self.log_error(f"Registration error: {str(e)}")
            return False
    
    def login_user(self, email: str, password: str) -> bool:
        """Login and get auth token"""
        self.log_info(f"Logging in: {email}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set auth header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                self.log_success("Login successful")
                self.log_info(f"Token: {self.token[:30]}...")
                return True
            else:
                self.log_error(f"Login failed: {response.status_code}")
                self.pretty_print_response(response)
                return False
                
        except Exception as e:
            self.log_error(f"Login error: {str(e)}")
            return False
    
    def get_profile(self) -> bool:
        """Get user profile"""
        self.log_info("Getting user profile")
        
        try:
            response = self.session.get(f"{BASE_URL}/profiles/me")
            
            if response.status_code == 200:
                self.log_success("Profile retrieved")
                self.pretty_print_response(response)
                return True
            else:
                self.log_error(f"Profile fetch failed: {response.status_code}")
                self.pretty_print_response(response)
                return False
                
        except Exception as e:
            self.log_error(f"Profile error: {str(e)}")
            return False
    
    def create_movie(self, title: str, duration_minutes: int = 120) -> Optional[int]:
        """Create a movie"""
        self.log_info(f"Creating movie: {title}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/movies/",
                json={
                    "title": title,
                    "duration_minutes": duration_minutes,
                    "description": f"Test movie: {title}",
                    "rating": "PG-13"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                movie_id = data.get("id")
                self.log_success(f"Movie created with ID: {movie_id}")
                return movie_id
            else:
                self.log_error(f"Movie creation failed: {response.status_code}")
                self.pretty_print_response(response)
                return None
                
        except Exception as e:
            self.log_error(f"Movie creation error: {str(e)}")
            return None
    
    def create_showtime(self, movie_id: int, screen_id: int) -> Optional[int]:
        """Create a showtime"""
        # Tomorrow at 7pm
        showtime = (datetime.now() + timedelta(days=1)).replace(
            hour=19, minute=0, second=0, microsecond=0
        )
        
        self.log_info(f"Creating showtime for movie {movie_id} at {showtime}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/showtimes/",
                json={
                    "movie_id": movie_id,
                    "screen_id": screen_id,
                    "start_time": showtime.isoformat()
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                showtime_id = data.get("id")
                self.log_success(f"Showtime created with ID: {showtime_id}")
                return showtime_id
            else:
                self.log_error(f"Showtime creation failed: {response.status_code}")
                self.pretty_print_response(response)
                return None
                
        except Exception as e:
            self.log_error(f"Showtime creation error: {str(e)}")
            return None
    
    def test_auth_flow(self):
        """Test authentication workflow"""
        self.log_section("TEST: Authentication Flow")
        
        email = f"test_{datetime.now().timestamp()}@example.com"
        password = "TestPassword123!"
        
        # 1. Register
        if not self.register_user(email, password):
            self.log_error("Auth flow failed at registration")
            return False
        
        # 2. Login
        if not self.login_user(email, password):
            self.log_error("Auth flow failed at login")
            return False
        
        # 3. Get profile
        if not self.get_profile():
            self.log_error("Auth flow failed at profile fetch")
            return False
        
        self.log_success("Auth flow completed successfully!")
        return True
    
    def test_movie_creation(self):
        """Test movie creation"""
        self.log_section("TEST: Movie Creation")
        
        movie_id = self.create_movie("The Matrix Reloaded")
        
        if movie_id:
            self.log_success("Movie creation test passed!")
            return movie_id
        else:
            self.log_error("Movie creation test failed!")
            return None
    
    def run_all_tests(self):
        """Run all workflow tests"""
        print(f"\n{Colors.BOLD}{'='*60}")
        print("Cinema Booking System - Workflow Tests")
        print(f"{'='*60}{Colors.RESET}\n")
        
        # Test 1: Auth
        if not self.test_auth_flow():
            self.log_error("Stopping tests - auth flow failed")
            return
        
        # Test 2: Movie creation
        movie_id = self.test_movie_creation()
        if not movie_id:
            self.log_error("Stopping tests - movie creation failed")
            return
        
        # More tests can be added here
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests completed!{Colors.RESET}\n")


def main():
    """Main entry point"""
    tester = CinemaAPITester()
    
    # You can run specific tests or all tests
    # tester.test_auth_flow()
    # tester.test_movie_creation()
    
    tester.run_all_tests()


if __name__ == "__main__":
    main()