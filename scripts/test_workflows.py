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
                data={"username": email, "password": password}
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
                    "age_rating": "PG-13"
                }
            )
            
            if response.status_code in [200, 201]:
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
    
    def create_layout(self, name: str, rows: int = 10, seats_per_row: int = 15) -> Optional[int]:
        """Create a seat layout"""
        self.log_info(f"Creating layout: {name}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/screen/layouts",
                json={
                    "name": name,
                    "rows": rows,
                    "seats_per_row": seats_per_row,
                    "grid": None  # Simple layout, no special seats
                }
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                layout_id = data.get("id")
                self.log_success(f"Layout created with ID: {layout_id}")
                return layout_id
            else:
                self.log_error(f"Layout creation failed: {response.status_code}")
                self.pretty_print_response(response)
                return None
                
        except Exception as e:
            self.log_error(f"Layout creation error: {str(e)}")
            return None
    
    def create_screen(self, name: str, layout_id: int, capacity: int = 150) -> Optional[int]:
        """Create a screen"""
        self.log_info(f"Creating screen: {name}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/screen/screens",
                json={
                    "name": name,
                    "capacity": capacity,
                    "seat_layout_id": layout_id
                }
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                screen_id = data.get("id")
                self.log_success(f"Screen created with ID: {screen_id}")
                return screen_id
            else:
                self.log_error(f"Screen creation failed: {response.status_code}")
                self.pretty_print_response(response)
                return None
                
        except Exception as e:
            self.log_error(f"Screen creation error: {str(e)}")
            return None
    
    def create_showtime(self, movie_id: int, screen_id: int, duration_minutes: int = 120, start_time: str = None) -> Optional[int]:
        """Create a showtime"""
        # Default to tomorrow at 7pm if no time provided
        if not start_time:
            tomorrow_7pm = (datetime.now() + timedelta(days=1)).replace(
                hour=19, minute=0, second=0, microsecond=0
            )
            start_time = tomorrow_7pm.isoformat()
        
        # Calculate end_time based on movie duration
        start_dt = datetime.fromisoformat(start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time = end_dt.isoformat()
        
        self.log_info(f"Creating showtime for movie {movie_id} on screen {screen_id}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/showtimes/",
                json={
                    "movie_id": movie_id,
                    "screen_id": screen_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "format": "2D"
                }
            )
            
            if response.status_code in [200, 201]:
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
    
    def get_seat_grid(self, showtime_id: int) -> bool:
        """Get seat availability grid for a showtime"""
        self.log_info(f"Getting seat grid for showtime {showtime_id}")
        
        try:
            response = self.session.get(f"{BASE_URL}/seatavailability/grid/{showtime_id}")
            
            if response.status_code == 200:
                self.log_success("Seat grid retrieved")
                self.pretty_print_response(response)
                return True
            else:
                self.log_error(f"Seat grid fetch failed: {response.status_code}")
                self.pretty_print_response(response)
                return False
                
        except Exception as e:
            self.log_error(f"Seat grid error: {str(e)}")
            return False
    
    def lock_seat(self, showtime_id: int, seat_code: str) -> bool:
        """Lock a seat"""
        self.log_info(f"Locking seat {seat_code} for showtime {showtime_id}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/seatavailability/lock",
                json={
                    "showtime_id": showtime_id,
                    "seat_code": seat_code
                }
            )
            
            if response.status_code in [200, 201]:
                self.log_success(f"Seat {seat_code} locked")
                return True
            else:
                self.log_error(f"Seat lock failed: {response.status_code}")
                self.pretty_print_response(response)
                return False
                
        except Exception as e:
            self.log_error(f"Seat lock error: {str(e)}")
            return False
    
    def create_reservation(self, showtime_id: int, seat_code: str) -> Optional[int]:
        """Create a reservation"""
        self.log_info(f"Creating reservation for seat {seat_code} at showtime {showtime_id}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/reservations/",
                json={
                    "showtime_id": showtime_id,
                    "seat_code": seat_code
                }
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                reservation_id = data.get("id")
                self.log_success(f"Reservation created with ID: {reservation_id}")
                return reservation_id
            else:
                self.log_error(f"Reservation creation failed: {response.status_code}")
                self.pretty_print_response(response)
                return None
                
        except Exception as e:
            self.log_error(f"Reservation creation error: {str(e)}")
            return None
    
    def get_orders(self) -> Optional[list]:
        """Get user's orders"""
        self.log_info("Getting orders")
        
        try:
            response = self.session.get(f"{BASE_URL}/orders/")
            
            if response.status_code == 200:
                data = response.json()
                self.log_success(f"Retrieved {len(data)} orders")
                self.pretty_print_response(response)
                return data
            else:
                self.log_error(f"Order fetch failed: {response.status_code}")
                self.pretty_print_response(response)
                return None
                
        except Exception as e:
            self.log_error(f"Order fetch error: {str(e)}")
            return None
    
    def initiate_payment(self, order_id: int) -> Optional[int]:
        """Initiate payment for an order"""
        self.log_info(f"Initiating payment for order {order_id}")
        
        try:
            response = self.session.post(f"{BASE_URL}/payments/order/{order_id}/initiate")
            
            if response.status_code in [200, 201]:
                data = response.json()
                payment_id = data.get("id")
                self.log_success(f"Payment initiated with ID: {payment_id}")
                self.pretty_print_response(response)
                return payment_id
            else:
                self.log_error(f"Payment initiation failed: {response.status_code}")
                self.pretty_print_response(response)
                return None
                
        except Exception as e:
            self.log_error(f"Payment initiation error: {str(e)}")
            return None
    
    def confirm_payment(self, payment_id: int) -> bool:
        """Confirm/complete a payment"""
        self.log_info(f"Confirming payment {payment_id}")
        
        try:
            response = self.session.post(f"{BASE_URL}/payments/{payment_id}/confirm")
            
            if response.status_code in [200, 201]:
                self.log_success(f"Payment {payment_id} confirmed!")
                self.pretty_print_response(response)
                return True
            else:
                self.log_error(f"Payment confirmation failed: {response.status_code}")
                self.pretty_print_response(response)
                return False
                
        except Exception as e:
            self.log_error(f"Payment confirmation error: {str(e)}")
            return False
    
    def get_payment_for_order(self, order_id: int) -> Optional[Dict]:
        """Get payment attempts for an order"""
        self.log_info(f"Getting payment for order {order_id}")
        
        try:
            response = self.session.get(f"{BASE_URL}/payments/order/{order_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_success("Payment info retrieved")
                self.pretty_print_response(response)
                return data
            else:
                self.log_error(f"Payment fetch failed: {response.status_code}")
                self.pretty_print_response(response)
                return None
                
        except Exception as e:
            self.log_error(f"Payment fetch error: {str(e)}")
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
        
        movie_title = f"The Matrix Reloaded {datetime.now().timestamp()}"
        movie_id = self.create_movie(movie_title)
        
        if movie_id:
            self.log_success("Movie creation test passed!")
            return movie_id
        else:
            self.log_error("Movie creation test failed!")
            return None
    
    def test_screen_setup(self):
        """Test screen and layout creation"""
        self.log_section("TEST: Screen Setup")
        
        # Create layout
        layout_name = f"Standard Layout {datetime.now().timestamp()}"
        layout_id = self.create_layout(layout_name, rows=10, seats_per_row=15)
        
        if not layout_id:
            self.log_error("Screen setup failed - couldn't create layout")
            return None, None
        
        # Create screen
        screen_name = f"Screen 1 {datetime.now().timestamp()}"
        screen_id = self.create_screen(screen_name, layout_id, capacity=150)
        
        if not screen_id:
            self.log_error("Screen setup failed - couldn't create screen")
            return layout_id, None
        
        self.log_success("Screen setup completed!")
        return layout_id, screen_id
    
    def test_showtime_creation(self, movie_id: int, screen_id: int):
        """Test showtime creation"""
        self.log_section("TEST: Showtime Creation")
        
        showtime_id = self.create_showtime(movie_id, screen_id, duration_minutes=120)
        
        if showtime_id:
            self.log_success("Showtime creation test passed!")
            return showtime_id
        else:
            self.log_error("Showtime creation test failed!")
            return None
    
    def test_seat_availability(self, showtime_id: int):
        """Test seat availability check"""
        self.log_section("TEST: Seat Availability")
        
        if self.get_seat_grid(showtime_id):
            self.log_success("Seat availability test passed!")
            return True
        else:
            self.log_error("Seat availability test failed!")
            return False
    
    def test_reservation_flow(self, showtime_id: int):
        """Test reservation creation"""
        self.log_section("TEST: Reservation Flow")
        
        # Try to reserve seat R5-8 (row 5, seat 8)
        seat_code = "R5-8"
        
        # Create reservation (this should also lock the seat)
        reservation_id = self.create_reservation(showtime_id, seat_code)
        
        if reservation_id:
            self.log_success("Reservation flow test passed!")
            return reservation_id
        else:
            self.log_error("Reservation flow test failed!")
            return None
    
    def test_order_payment_flow(self, reservation_id: int):
        """Test order and payment creation"""
        self.log_section("TEST: Order & Payment Flow")
        
        # Get orders (should include one for our reservation)
        orders = self.get_orders()
        
        if not orders:
            self.log_error("No orders found - order may not have been created automatically")
            return None
        
        # Find the order for our reservation
        order = None
        for o in orders:
            if o.get("reservation_id") == reservation_id:
                order = o
                break
        
        if not order:
            self.log_error(f"Order for reservation {reservation_id} not found")
            return None
        
        order_id = order.get("id")
        self.log_success(f"Found order {order_id} for reservation {reservation_id}")
        
        # Initiate payment
        payment_id = self.initiate_payment(order_id)
        if not payment_id:
            self.log_error("Failed to initiate payment")
            return None
        
        # Confirm payment (mock payment success)
        if not self.confirm_payment(payment_id):
            self.log_error("Failed to confirm payment")
            return None
        
        # Verify order is now completed
        orders = self.get_orders()
        updated_order = None
        for o in orders:
            if o.get("id") == order_id:
                updated_order = o
                break
        
        if updated_order and updated_order.get("is_completed"):
            self.log_success("Order marked as completed after payment!")
        else:
            self.log_error("Order not marked as completed")
            return None
        
        self.log_success("Full Order & Payment flow test passed!")
        return order_id
    
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
        
        # Test 3: Screen setup
        layout_id, screen_id = self.test_screen_setup()
        if not screen_id:
            self.log_error("Stopping tests - screen setup failed")
            return
        
        # Test 4: Showtime creation
        showtime_id = self.test_showtime_creation(movie_id, screen_id)
        if not showtime_id:
            self.log_error("Stopping tests - showtime creation failed")
            return
        
        # Test 5: Seat availability
        if not self.test_seat_availability(showtime_id):
            self.log_error("Stopping tests - seat availability check failed")
            return
        
        # Test 6: Reservation
        reservation_id = self.test_reservation_flow(showtime_id)
        if not reservation_id:
            self.log_error("Stopping tests - reservation flow failed")
            return
        
        # Test 7: Order & Payment (FULL FLOW!)
        order_id = self.test_order_payment_flow(reservation_id)
        if not order_id:
            self.log_error("Stopping tests - order & payment flow failed")
            return
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! FULL BOOKING WORKFLOW COMPLETE! 🎉{Colors.RESET}\n")


def main():
    """Main entry point"""
    tester = CinemaAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()