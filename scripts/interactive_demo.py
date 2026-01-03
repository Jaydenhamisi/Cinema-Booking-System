"""
Interactive CLI demo for Cinema Booking System
Demonstrates the full booking flow using the actual API
"""

import requests
from datetime import datetime
from typing import Optional

BASE_URL = "http://localhost:8000"


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class CinemaBookingCLI:
    def __init__(self):
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def print_header(self, text: str):
        """Print a section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}{Colors.RESET}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.RESET}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")
    
    def login(self):
        """Login or register user"""
        self.print_header("🎬 Welcome to Cinema Booking System")
        
        print("1. Login")
        print("2. Register new account")
        choice = input("\nChoose option (1/2): ").strip()
        
        email = input("Email: ").strip()
        password = input("Password (min 8 chars): ").strip()
        
        try:
            if choice == "2":
                # Register
                response = self.session.post(
                    f"{BASE_URL}/auth/register",
                    json={"email": email, "password": password}
                )
            else:
                # Login
                form_data = f"username={email}&password={password}"
                response = self.session.post(
                    f"{BASE_URL}/auth/login",
                    data=form_data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.token = data['access_token']
                self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                self.print_success(f"Logged in as {email}")
                return True
            else:
                self.print_error(f"Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error: {e}")
            return False
    
    def show_movies(self):
        """Display all available movies"""
        self.print_header("🎬 Available Movies")
        
        try:
            response = self.session.get(f"{BASE_URL}/movies/")
            
            if response.status_code == 200:
                movies = response.json()
                
                if not movies:
                    self.print_info("No movies available")
                    return []
                
                for i, movie in enumerate(movies, 1):
                    status = "✓ Active" if movie['is_active'] else "✗ Inactive"
                    print(f"\n{Colors.BOLD}{i}. {movie['title']}{Colors.RESET}")
                    print(f"   Duration: {movie['duration_minutes']} min | Rating: {movie['age_rating']}")
                    print(f"   {movie.get('description', 'No description')}")
                    print(f"   Status: {status}")
                
                return movies
            else:
                self.print_error(f"Failed to fetch movies: {response.status_code}")
                return []
                
        except Exception as e:
            self.print_error(f"Error: {e}")
            return []
    
    def show_showtimes(self, movie_id: int):
        """Display showtimes for a movie"""
        self.print_header("🎞️  Available Showtimes")
        
        try:
            response = self.session.get(f"{BASE_URL}/showtimes/movie/{movie_id}")
            
            if response.status_code == 200:
                showtimes = response.json()
                
                if not showtimes:
                    self.print_info("No showtimes available for this movie")
                    return []
                
                for i, showtime in enumerate(showtimes, 1):
                    start = datetime.fromisoformat(showtime['start_time'])
                    print(f"\n{Colors.BOLD}{i}. {start.strftime('%Y-%m-%d %H:%M')}{Colors.RESET}")
                    print(f"   Screen: {showtime['screen_id']} | Format: {showtime['format']}")
                
                return showtimes
            else:
                self.print_error(f"Failed to fetch showtimes: {response.status_code}")
                return []
                
        except Exception as e:
            self.print_error(f"Error: {e}")
            return []
    
    def display_seat_grid(self, showtime_id: int):
        """Display visual seat grid with availability"""
        try:
            # Get seat availability
            response = self.session.get(f"{BASE_URL}/seatavailability/grid/{showtime_id}")
            
            if response.status_code != 200:
                self.print_info("Could not load seat grid")
                return None
            
            data = response.json()
            seats = data.get('seats', [])
            
            if not seats:
                self.print_info("No seat information available")
                return None
            
            # Organize seats by row
            seat_map = {}
            for seat in seats:
                code = seat['seat_code']
                try:
                    row, num = code.split('-')
                    if row not in seat_map:
                        seat_map[row] = []
                    seat_map[row].append({
                        'code': code,
                        'num': int(num),
                        'status': seat['status']
                    })
                except:
                    continue
            
            # Sort rows and seats
            rows = sorted(seat_map.keys())
            for row in rows:
                seat_map[row].sort(key=lambda x: x['num'])
            
            # Display grid
            print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
            print("                           🎬 SCREEN")
            print(f"{'='*70}{Colors.RESET}\n")
            
            for row in rows:
                # Separate left and right sections (aisle in middle)
                mid = len(seat_map[row]) // 2
                left_section = seat_map[row][:mid]
                right_section = seat_map[row][mid:]
                
                # Build left section
                left_display = ""
                for seat in left_section:
                    status = seat['status']
                    if status == 'available':
                        symbol = f"{Colors.GREEN}◯{Colors.RESET}"
                    elif status == 'locked':
                        symbol = f"{Colors.YELLOW}◐{Colors.RESET}"
                    elif status == 'reserved':
                        symbol = f"{Colors.RED}●{Colors.RESET}"
                    else:
                        symbol = "?"
                    left_display += symbol + " "
                
                # Build right section
                right_display = ""
                for seat in right_section:
                    status = seat['status']
                    if status == 'available':
                        symbol = f"{Colors.GREEN}◯{Colors.RESET}"
                    elif status == 'locked':
                        symbol = f"{Colors.YELLOW}◐{Colors.RESET}"
                    elif status == 'reserved':
                        symbol = f"{Colors.RED}●{Colors.RESET}"
                    else:
                        symbol = "?"
                    right_display += symbol + " "
                
                # Print row with aisle
                print(f"   {Colors.BOLD}{row}{Colors.RESET}  {left_display}   {Colors.CYAN}|{Colors.RESET}   {right_display}")
            
            print(f"\n{'-'*70}")
            print(f"   {Colors.GREEN}◯{Colors.RESET} Available   "
                  f"{Colors.YELLOW}◐{Colors.RESET} Locked   "
                  f"{Colors.RED}●{Colors.RESET} Reserved")
            print(f"{'-'*70}\n")
            
            return seats
        
        except Exception as e:
            self.print_error(f"Error displaying grid: {e}")
            return None
    
    def get_seat_stats(self, showtime_id: int):
        """Get seat availability statistics"""
        try:
            response = self.session.get(f"{BASE_URL}/seatavailability/grid/{showtime_id}")
            
            if response.status_code == 200:
                data = response.json()
                seats = data.get('seats', [])
                
                available = sum(1 for s in seats if s['status'] == 'available')
                locked = sum(1 for s in seats if s['status'] == 'locked')
                reserved = sum(1 for s in seats if s['status'] == 'reserved')
                
                print(f"{Colors.GREEN}Available: {available}{Colors.RESET} | ", end='')
                print(f"{Colors.YELLOW}Locked: {locked}{Colors.RESET} | ", end='')
                print(f"{Colors.RED}Reserved: {reserved}{Colors.RESET}\n")
                
                return seats
            else:
                return []
                
        except Exception as e:
            self.print_error(f"Error: {e}")
            return []
    
    def create_reservation(self, showtime_id: int, seat_code: str):
        """Create a reservation"""
        try:
            response = self.session.post(
                f"{BASE_URL}/reservations/",
                json={"showtime_id": showtime_id, "seat_code": seat_code}
            )
            
            if response.status_code == 200:
                reservation = response.json()
                self.print_success(f"Reservation created! ID: {reservation['id']}")
                return reservation
            else:
                self.print_error(f"Reservation failed: {response.text}")
                return None
                
        except Exception as e:
            self.print_error(f"Error: {e}")
            return None
    
    def get_orders(self):
        """Get user's orders"""
        try:
            response = self.session.get(f"{BASE_URL}/orders/")
            
            if response.status_code == 200:
                return response.json()
            else:
                self.print_error(f"Failed to fetch orders: {response.status_code}")
                return []
                
        except Exception as e:
            self.print_error(f"Error: {e}")
            return []
    
    def complete_booking(self, reservation_id: int):
        """Complete the booking by paying"""
        self.print_header("💳 Payment")
        
        # Get order for this reservation
        orders = self.get_orders()
        order = next((o for o in orders if o['reservation_id'] == reservation_id), None)
        
        if not order:
            self.print_error("Order not found")
            return False
        
        order_id = order['id']
        amount = order['final_amount']
        
        print(f"Total: £{amount/100:.2f}")
        confirm = input("\nProceed with payment? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            self.print_info("Payment cancelled")
            return False
        
        try:
            # Initiate payment
            response = self.session.post(f"{BASE_URL}/payments/order/{order_id}/initiate")
            
            if response.status_code != 200:
                self.print_error(f"Payment initiation failed: {response.text}")
                return False
            
            payment = response.json()
            payment_id = payment['id']
            
            # Confirm payment (mock)
            response = self.session.post(f"{BASE_URL}/payments/{payment_id}/confirm")
            
            if response.status_code == 200:
                payment_data = response.json()
                if payment_data['status'] == 'succeeded':
                    self.print_success("Payment successful! Booking confirmed!")
                    return True
                else:
                    self.print_error(f"Payment failed: {payment_data.get('failure_reason', 'Unknown')}")
                    return False
            else:
                self.print_error(f"Payment confirmation failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error: {e}")
            return False
    
    def booking_flow(self):
        """Main booking flow"""
        # Show movies
        movies = self.show_movies()
        if not movies:
            return
        
        # Select movie
        while True:
            try:
                choice = int(input("\nSelect movie number (0 to exit): "))
                if choice == 0:
                    return
                if 1 <= choice <= len(movies):
                    selected_movie = movies[choice - 1]
                    break
                else:
                    self.print_error("Invalid choice")
            except ValueError:
                self.print_error("Please enter a number")
        
        # Show showtimes
        showtimes = self.show_showtimes(selected_movie['id'])
        if not showtimes:
            return
        
        # Select showtime
        while True:
            try:
                choice = int(input("\nSelect showtime number (0 to exit): "))
                if choice == 0:
                    return
                if 1 <= choice <= len(showtimes):
                    selected_showtime = showtimes[choice - 1]
                    break
                else:
                    self.print_error("Invalid choice")
            except ValueError:
                self.print_error("Please enter a number")
        
        # Show seat grid and availability
        self.print_header("🪑 Seat Selection")
        
        # Display visual grid
        self.display_seat_grid(selected_showtime['id'])
        
        # Show statistics
        self.get_seat_stats(selected_showtime['id'])
        
        # Enter seat code
        seat_code = input("Enter seat code (e.g., A-5): ").strip().upper()
        
        # Create reservation
        reservation = self.create_reservation(selected_showtime['id'], seat_code)
        if not reservation:
            return
        
        # Complete payment
        if self.complete_booking(reservation['id']):
            self.print_header("🎉 Booking Complete!")
            print(f"Movie: {selected_movie['title']}")
            print(f"Showtime: {datetime.fromisoformat(selected_showtime['start_time']).strftime('%Y-%m-%d %H:%M')}")
            print(f"Seat: {seat_code}")
            print("\nEnjoy your movie! 🍿")
    
    def main_menu(self):
        """Main menu loop"""
        while True:
            self.print_header("📋 Main Menu")
            print("1. Book a ticket")
            print("2. View my bookings")
            print("3. Exit")
            
            choice = input("\nChoose option: ").strip()
            
            if choice == "1":
                self.booking_flow()
            elif choice == "2":
                self.view_bookings()
            elif choice == "3":
                print(f"\n{Colors.CYAN}Thanks for using Cinema Booking System! 👋{Colors.RESET}\n")
                break
            else:
                self.print_error("Invalid choice")
    
    def view_bookings(self):
        """View user's bookings"""
        self.print_header("📋 My Bookings")
        
        try:
            response = self.session.get(f"{BASE_URL}/reservations/")
            
            if response.status_code == 200:
                reservations = response.json()
                
                if not reservations:
                    self.print_info("No bookings found")
                    return
                
                for res in reservations:
                    status_color = Colors.GREEN if res['status'] == 'active' else Colors.RED
                    print(f"\n{Colors.BOLD}Reservation #{res['id']}{Colors.RESET}")
                    print(f"Seat: {res['seat_code']} | Status: {status_color}{res['status']}{Colors.RESET}")
                    print(f"Showtime ID: {res['showtime_id']}")
            else:
                self.print_error(f"Failed to fetch bookings: {response.status_code}")
                
        except Exception as e:
            self.print_error(f"Error: {e}")
    
    def run(self):
        """Start the CLI"""
        if self.login():
            self.main_menu()


if __name__ == "__main__":
    cli = CinemaBookingCLI()
    cli.run()