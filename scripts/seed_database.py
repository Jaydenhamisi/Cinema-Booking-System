"""
Seed the database with test data for demo purposes
"""

import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


def create_admin_user():
    """Create admin user and return auth token"""
    print("Creating admin user...")
    
    email = "admin@cinema.com"
    password = "admin123456"
    
    try:
        # Try to register
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password}
        )
        
        if response.status_code in [200, 201]:
            print(f"✓ Admin user created: {email}")
            data = response.json()
            return data['access_token']
        else:
            # User might already exist, try login
            print("Admin user exists, logging in...")
            form_data = f"username={email}&password={password}"
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                print(f"✓ Logged in as: {email}")
                data = response.json()
                return data['access_token']
            else:
                print(f"✗ Failed to authenticate: {response.text}")
                return None
                
    except Exception as e:
        print(f"✗ Error creating admin: {e}")
        return None


def promote_to_admin(email: str):
    """Promote user to admin via direct database update"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cinema_db",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Update user_credentials table
        cursor.execute(
            "UPDATE user_credentials SET user_type = 'admin' WHERE email = %s",
            (email,)
        )
        
        # Update user_profiles table
        cursor.execute(
            "UPDATE user_profiles SET user_type = 'ADMIN' WHERE email = %s",
            (email,)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Promoted {email} to admin")
        return True
        
    except Exception as e:
        print(f"✗ Failed to promote user: {e}")
        return False


def seed_movies(token: str):
    """Create sample movies"""
    print("\nSeeding movies...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    movies = [
        {
            "title": "The Matrix",
            "description": "A computer hacker learns about the true nature of reality",
            "duration_minutes": 136,
            "age_rating": "R",
            "release_date": "1999-03-31"
        },
        {
            "title": "Inception",
            "description": "A thief who steals corporate secrets through dream-sharing",
            "duration_minutes": 148,
            "age_rating": "PG-13",
            "release_date": "2010-07-16"
        },
        {
            "title": "Interstellar",
            "description": "A team of explorers travel through a wormhole in space",
            "duration_minutes": 169,
            "age_rating": "PG-13",
            "release_date": "2014-11-07"
        },
        {
            "title": "The Dark Knight",
            "description": "Batman faces the Joker in Gotham City",
            "duration_minutes": 152,
            "age_rating": "PG-13",
            "release_date": "2008-07-18"
        }
    ]
    
    movie_ids = []
    
    for movie_data in movies:
        try:
            response = requests.post(
                f"{BASE_URL}/movies/",
                headers=headers,
                json=movie_data
            )
            
            if response.status_code in [200, 201]:
                movie = response.json()
                movie_ids.append(movie['id'])
                print(f"✓ Created movie: {movie_data['title']} (ID: {movie['id']})")
            else:
                print(f"✗ Failed to create {movie_data['title']}: {response.text}")
                
        except Exception as e:
            print(f"✗ Error creating movie: {e}")
    
    return movie_ids


def generate_seat_grid(rows, seats_per_row):
    """Generate a cinema-style seat grid with center aisle"""
    row_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    grid = {}
    
    for row_idx in range(rows):
        row = row_letters[row_idx]
        seats = []
        
        # Left section
        for seat_num in range(1, (seats_per_row // 2) + 1):
            seats.append(f"{row}-{seat_num}")
        
        # Center aisle
        seats.append("AISLE")
        
        # Right section
        for seat_num in range((seats_per_row // 2) + 1, seats_per_row + 1):
            seats.append(f"{row}-{seat_num}")
        
        grid[row] = seats
    
    return grid


def seed_layouts(token: str):
    """Create sample seat layouts"""
    print("\nSeeding seat layouts...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    layouts = [
        {
            "name": "Standard Layout",
            "rows": 8,
            "seats_per_row": 12,
            "grid": generate_seat_grid(8, 12)
        },
        {
            "name": "Large Screen Layout",
            "rows": 10,
            "seats_per_row": 16,
            "grid": generate_seat_grid(10, 16)
        }
    ]
    
    layout_ids = []
    
    for layout_data in layouts:
        try:
            response = requests.post(
                f"{BASE_URL}/screen/layouts",
                headers=headers,
                json=layout_data
            )
            
            if response.status_code in [200, 201]:
                layout = response.json()
                layout_ids.append(layout['id'])
                print(f"✓ Created layout: {layout_data['name']} (ID: {layout['id']}) - {layout_data['rows']}x{layout_data['seats_per_row']} = {layout_data['rows'] * layout_data['seats_per_row']} seats")
            else:
                print(f"✗ Failed to create {layout_data['name']}: {response.text}")
                
        except Exception as e:
            print(f"✗ Error creating layout: {e}")
    
    return layout_ids


def seed_screens(token: str, layout_ids: list):
    """Create sample screens"""
    print("\nSeeding screens...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    if not layout_ids:
        print("✗ No layouts available")
        return []
    
    screens = [
        {
            "name": "Screen 1",
            "capacity": 96,
            "seat_layout_id": layout_ids[0]
        },
        {
            "name": "Screen 2",
            "capacity": 96,
            "seat_layout_id": layout_ids[0]
        },
        {
            "name": "IMAX Screen",
            "capacity": 160,
            "seat_layout_id": layout_ids[1] if len(layout_ids) > 1 else layout_ids[0]
        }
    ]
    
    screen_ids = []
    
    for screen_data in screens:
        try:
            response = requests.post(
                f"{BASE_URL}/screen/screens",
                headers=headers,
                json=screen_data
            )
            
            if response.status_code in [200, 201]:
                screen = response.json()
                screen_ids.append(screen['id'])
                print(f"✓ Created screen: {screen_data['name']} (ID: {screen['id']})")
            else:
                print(f"✗ Failed to create {screen_data['name']}: {response.text}")
                
        except Exception as e:
            print(f"✗ Error creating screen: {e}")
    
    return screen_ids


def seed_showtimes(token: str, movie_ids: list, screen_ids: list):
    """Create sample showtimes - ALL movies get showtimes with NO conflicts"""
    print("\nSeeding showtimes...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    if not movie_ids or not screen_ids:
        print("✗ No movies or screens available")
        return []
    
    base_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    formats = ["2D", "3D", "IMAX_2D"]
    showtime_ids = []
    
    # Strategy: Give each movie showtimes across 3 days
    # Spread movies across screens to avoid conflicts
    for day_offset in range(3):  # 3 days
        for movie_idx, movie_id in enumerate(movie_ids):  # ALL 4 movies
            # Assign to a screen (cycle through available screens)
            screen_id = screen_ids[movie_idx % len(screen_ids)]
            
            # Calculate which "slot" this movie has on this screen
            # (e.g., if 2 movies share a screen, slot 0 and slot 1)
            movies_on_this_screen = [i for i in range(len(movie_ids)) if i % len(screen_ids) == movie_idx % len(screen_ids)]
            slot_on_screen = movies_on_this_screen.index(movie_idx)
            
            # Stagger times: each slot gets 3.5 hours (movie is ~2.5h + 1h buffer)
            # Slot 0: 12pm, Slot 1: 3:30pm, Slot 2: 7pm
            hour_offset = slot_on_screen * 3.5
            
            start_time = base_date + timedelta(days=day_offset, hours=hour_offset)
            end_time = start_time + timedelta(hours=2, minutes=30)
            
            showtime_data = {
                "movie_id": movie_id,
                "screen_id": screen_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "format": formats[screen_id % len(formats)]
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/showtimes/",
                    headers=headers,
                    json=showtime_data
                )
                
                if response.status_code in [200, 201]:
                    showtime = response.json()
                    showtime_ids.append(showtime['id'])
                    print(f"✓ Created showtime: Movie {movie_id}, Screen {screen_id} @ {start_time.strftime('%Y-%m-%d %H:%M')}")
                else:
                    print(f"✗ Failed to create showtime: {response.text}")
                    
            except Exception as e:
                print(f"✗ Error creating showtime: {e}")
    
    return showtime_ids


def seed_pricing_modifiers(token: str):
    """Create sample pricing modifiers"""
    print("\nSeeding pricing modifiers...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    modifiers = [
        {
            "name": "Base Price",
            "modifier_type": "additive",
            "amount": 1000,  # £10.00 in pence
            "is_active": True,
            "applies_to": None
        },
        {
            "name": "Weekend Surcharge",
            "modifier_type": "additive",
            "amount": 200,  # £2.00
            "is_active": True,
            "applies_to": {"days": ["Saturday", "Sunday"]}
        }
    ]
    
    for modifier_data in modifiers:
        try:
            response = requests.post(
                f"{BASE_URL}/pricing/modifiers",
                headers=headers,
                json=modifier_data
            )
            
            if response.status_code in [200, 201]:
                modifier = response.json()
                print(f"✓ Created modifier: {modifier_data['name']} (ID: {modifier['id']})")
            else:
                print(f"✗ Failed to create {modifier_data['name']}: {response.text}")
                
        except Exception as e:
            print(f"✗ Error creating modifier: {e}")


def main():
    """Main seeding function"""
    print("="*60)
    print("Cinema Booking System - Database Seeding")
    print("="*60)
    
    # Create admin user
    token = create_admin_user()
    if not token:
        print("\n✗ Failed to create admin user. Exiting.")
        return
    
    # Promote to admin
    promote_to_admin("admin@cinema.com")
    
    # Seed data
    movie_ids = seed_movies(token)
    layout_ids = seed_layouts(token)
    screen_ids = seed_screens(token, layout_ids)
    showtime_ids = seed_showtimes(token, movie_ids, screen_ids)
    seed_pricing_modifiers(token)
    
    print("\n" + "="*60)
    print("✓ Database seeding complete!")
    print("="*60)
    print(f"\nCreated:")
    print(f"  - {len(movie_ids)} movies")
    print(f"  - {len(layout_ids)} layouts")
    print(f"  - {len(screen_ids)} screens")
    print(f"  - {len(showtime_ids)} showtimes")
    print(f"\nAdmin credentials:")
    print(f"  Email: admin@cinema.com")
    print(f"  Password: admin123456")
    print(f"\nValid seat examples:")
    print(f"  Standard Layout (8 rows x 12 seats): A-1 to H-12")
    print(f"  Large Layout (10 rows x 16 seats): A-1 to J-16")
    print(f"  Note: Center aisle between left and right sections")
    print()


if __name__ == "__main__":
    main()