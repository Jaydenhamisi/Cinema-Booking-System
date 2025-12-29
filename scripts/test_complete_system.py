# scripts/test_complete_system.py

import time
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Test results tracking
tests_passed = 0
tests_failed = 0

def log(emoji, message):
    print(f"{emoji} {message}")

def test_result(name, passed):
    global tests_passed, tests_failed
    if passed:
        tests_passed += 1
        log("✅", f"{name} PASSED")
    else:
        tests_failed += 1
        log("❌", f"{name} FAILED")
    print()

# ============================================================
# SETUP FUNCTIONS
# ============================================================

def create_user(email_suffix):
    """Create and login a test user"""
    email = f"test_{email_suffix}@example.com"
    password = "testpassword123"
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password}
        )
        
        if response.status_code != 201:
            log("⚠️", f"Registration failed [{response.status_code}]: {response.text}")
            return None
            
        data = response.json()
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        return {"email": email, "token": token, "headers": headers}
        
    except Exception as e:
        log("⚠️", f"User creation error: {e}")
        return None

def promote_to_admin(user_email):
    """Promote a user to admin via direct database update"""
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
        cursor.execute(
            "UPDATE user_credentials SET user_type = 'admin' WHERE email = %s",
            (user_email,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        log("👑", f"Promoted {user_email} to admin")
        return True
    except Exception as e:
        log("⚠️", f"Failed to promote user: {e}")
        return False

def create_test_showtime():
    """Create movie, screen, layout, showtime for testing"""
    timestamp = time.time()
    
    try:
        # Create admin user
        admin = create_user(f"admin_{timestamp}")
        if not admin:
            raise Exception("Failed to create admin user")
        
        # Promote to admin
        if not promote_to_admin(admin["email"]):
            raise Exception("Failed to promote user to admin")
        
        # Create movie
        movie_response = requests.post(
            f"{BASE_URL}/movies/",
            headers=admin["headers"],
            json={
                "title": f"Test Movie {timestamp}",
                "description": "Test movie",
                "duration_minutes": 120,
                "age_rating": "PG-13"
            }
        )
        
        if movie_response.status_code != 200:
            raise Exception(f"Movie creation failed [{movie_response.status_code}]: {movie_response.text}")
        
        movie_id = movie_response.json()["id"]
        
        # Create layout
        layout_response = requests.post(
            f"{BASE_URL}/screen/layouts",
            headers=admin["headers"],
            json={
                "name": f"Test Layout {timestamp}",
                "rows": 10,
                "seats_per_row": 15
            }
        )
        
        if layout_response.status_code != 201:
            raise Exception(f"Layout creation failed [{layout_response.status_code}]: {layout_response.text}")
        
        layout_id = layout_response.json()["id"]
        
        # Create screen
        screen_response = requests.post(
            f"{BASE_URL}/screen/screens",
            headers=admin["headers"],
            json={
                "name": f"Test Screen {timestamp}",
                "capacity": 150,
                "seat_layout_id": layout_id
            }
        )
        
        if screen_response.status_code != 201:
            raise Exception(f"Screen creation failed [{screen_response.status_code}]: {screen_response.text}")
        
        screen_id = screen_response.json()["id"]
        
        # Create showtime (tomorrow)
        tomorrow = (datetime.now() + timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)
        showtime_response = requests.post(
            f"{BASE_URL}/showtimes/",
            headers=admin["headers"],
            json={
                "movie_id": movie_id,
                "screen_id": screen_id,
                "start_time": tomorrow.isoformat(),
                "end_time": (tomorrow + timedelta(hours=2)).isoformat(),
                "format": "2D"
            }
        )
        
        if showtime_response.status_code != 201:
            raise Exception(f"Showtime creation failed [{showtime_response.status_code}]: {showtime_response.text}")
        
        showtime_id = showtime_response.json()["id"]
        
        return {
            "showtime_id": showtime_id,
            "movie_id": movie_id,
            "screen_id": screen_id,
            "admin": admin
        }
        
    except Exception as e:
        log("⚠️", f"Setup error: {e}")
        raise

# ============================================================
# TEST 1: NORMAL BOOKING FLOW
# ============================================================

def test_normal_booking_flow():
    log("🎬", "TEST 1: Normal Booking Flow")
    
    try:
        # Setup
        setup = create_test_showtime()
        user = create_user(f"booking_{time.time()}")
        
        if not user:
            raise Exception("Failed to create user")
        
        # Reserve seat
        log("📍", "Creating reservation...")
        reservation_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=user["headers"],
            json={
                "showtime_id": setup["showtime_id"],
                "seat_code": "R5-5"
            }
        )
        
        if reservation_response.status_code != 200:
            raise Exception(f"Reservation failed [{reservation_response.status_code}]: {reservation_response.text}")
        
        reservation_id = reservation_response.json()["id"]
        log("✓", f"Reservation created: {reservation_id}")
        
        # Get order
        log("📦", "Getting order...")
        orders_response = requests.get(
            f"{BASE_URL}/orders/",
            headers=user["headers"]
        )
        
        if orders_response.status_code != 200:
            raise Exception(f"Get orders failed [{orders_response.status_code}]: {orders_response.text}")
        
        orders = orders_response.json()
        order = next((o for o in orders if o["reservation_id"] == reservation_id), None)
        
        if not order:
            raise Exception(f"Order not found for reservation {reservation_id}")
        
        order_id = order["id"]
        log("✓", f"Order found: {order_id}")
        
        # Initiate payment
        log("💳", "Initiating payment...")
        payment_response = requests.post(
            f"{BASE_URL}/payments/order/{order_id}/initiate",
            headers=user["headers"]
        )
        
        if payment_response.status_code != 200:
            raise Exception(f"Payment initiation failed [{payment_response.status_code}]: {payment_response.text}")
        
        payment_id = payment_response.json()["id"]
        log("✓", f"Payment initiated: {payment_id}")
        
        # Confirm payment
        log("✅", "Confirming payment...")
        confirm_response = requests.post(
            f"{BASE_URL}/payments/{payment_id}/confirm",
            headers=user["headers"]
        )
        
        if confirm_response.status_code != 200:
            raise Exception(f"Payment confirmation failed [{confirm_response.status_code}]: {confirm_response.text}")
        
        payment_data = confirm_response.json()
        
        if payment_data["status"] != "succeeded":
            raise Exception(f"Payment status is {payment_data['status']}, expected 'succeeded'")
        
        log("✓", "Payment confirmed")
        
        # Verify order completed
        log("🔍", "Verifying order completion...")
        orders_response = requests.get(
            f"{BASE_URL}/orders/",
            headers=user["headers"]
        )
        
        order = next((o for o in orders_response.json() if o["id"] == order_id), None)
        
        if not order:
            raise Exception("Order not found after payment")
        
        if not order["is_completed"]:
            raise Exception(f"Order not completed: {order}")
        
        log("✓", "Order completed successfully")
        
        test_result("Normal Booking Flow", True)
        return True
        
    except Exception as e:
        log("❌", f"Error: {str(e)}")
        test_result("Normal Booking Flow", False)
        return False

# ============================================================
# TEST 2: USER CANCELLATION FLOW
# ============================================================

def test_user_cancellation_flow():
    log("🚫", "TEST 2: User Cancellation Flow")
    
    try:
        # Setup
        setup = create_test_showtime()
        user = create_user(f"cancel_{time.time()}")
        
        if not user:
            raise Exception("Failed to create user")
        
        # Reserve seat
        log("📍", "Creating reservation...")
        reservation_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=user["headers"],
            json={
                "showtime_id": setup["showtime_id"],
                "seat_code": "R6-6"
            }
        )
        
        if reservation_response.status_code != 200:
            raise Exception(f"Reservation failed: {reservation_response.text}")
        
        reservation_id = reservation_response.json()["id"]
        log("✓", f"Reservation created: {reservation_id}")
        
        # Get order and pay
        orders_response = requests.get(f"{BASE_URL}/orders/", headers=user["headers"])
        order = next((o for o in orders_response.json() if o["reservation_id"] == reservation_id), None)
        
        if not order:
            raise Exception("Order not found")
        
        log("💳", "Paying for order...")
        payment_response = requests.post(
            f"{BASE_URL}/payments/order/{order['id']}/initiate",
            headers=user["headers"]
        )
        payment_id = payment_response.json()["id"]
        
        confirm_response = requests.post(
            f"{BASE_URL}/payments/{payment_id}/confirm",
            headers=user["headers"]
        )
        
        if confirm_response.json()["status"] != "succeeded":
            raise Exception("Payment did not succeed")
        
        log("✓", "Payment completed")
        
        # CANCEL RESERVATION
        log("🚫", "Cancelling reservation...")
        cancel_response = requests.post(
            f"{BASE_URL}/reservations/{reservation_id}/cancel",
            headers=user["headers"]
        )
        
        if cancel_response.status_code != 200:
            raise Exception(f"Cancellation failed [{cancel_response.status_code}]: {cancel_response.text}")
        
        cancelled_reservation = cancel_response.json()
        
        if cancelled_reservation["status"] != "cancelled":
            raise Exception(f"Reservation status is {cancelled_reservation['status']}, expected 'cancelled'")
        
        log("✓", "Reservation cancelled successfully")
        
        test_result("User Cancellation Flow", True)
        return True
        
    except Exception as e:
        log("❌", f"Error: {str(e)}")
        test_result("User Cancellation Flow", False)
        return False

# ============================================================
# TEST 3: PAYMENT FAILURE FLOW
# ============================================================

def test_payment_failure_flow():
    log("💳", "TEST 3: Payment Failure Flow")
    
    try:
        # Setup
        setup = create_test_showtime()
        user = create_user(f"failpay_{time.time()}")
        
        if not user:
            raise Exception("Failed to create user")
        
        # Reserve seat
        log("📍", "Creating reservation...")
        reservation_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=user["headers"],
            json={
                "showtime_id": setup["showtime_id"],
                "seat_code": "R7-7"
            }
        )
        
        if reservation_response.status_code != 200:
            raise Exception(f"Reservation failed: {reservation_response.text}")
        
        reservation_id = reservation_response.json()["id"]
        log("✓", f"Reservation created: {reservation_id}")
        
        # Get order
        orders_response = requests.get(f"{BASE_URL}/orders/", headers=user["headers"])
        order = next((o for o in orders_response.json() if o["reservation_id"] == reservation_id), None)
        
        if not order:
            raise Exception("Order not found")
        
        # Initiate payment
        log("💳", "Initiating payment...")
        payment_response = requests.post(
            f"{BASE_URL}/payments/order/{order['id']}/initiate",
            headers=user["headers"]
        )
        payment_id = payment_response.json()["id"]
        log("✓", f"Payment initiated: {payment_id}")
        
        # FAIL PAYMENT (admin force fail)
        log("❌", "Admin forcing payment failure...")
        fail_response = requests.post(
            f"{BASE_URL}/admin/payments/{payment_id}/fail",
            headers=setup["admin"]["headers"]
        )
        
        if fail_response.status_code != 200:
            raise Exception(f"Payment fail request failed [{fail_response.status_code}]: {fail_response.text}")
        
        log("✓", "Payment failed by admin")
        
        # Verify order not completed
        log("🔍", "Verifying order not completed...")
        orders_response = requests.get(f"{BASE_URL}/orders/", headers=user["headers"])
        order = next((o for o in orders_response.json() if o["id"] == order["id"]), None)
        
        if not order:
            raise Exception("Order not found")
        
        if order["is_completed"]:
            raise Exception("Order should not be completed after payment failure")
        
        log("✓", "Order correctly not completed")
        
        test_result("Payment Failure Flow", True)
        return True
        
    except Exception as e:
        log("❌", f"Error: {str(e)}")
        test_result("Payment Failure Flow", False)
        return False

# ============================================================
# TEST 4: ADMIN FORCE CANCEL
# ============================================================

def test_admin_force_cancel():
    log("👮", "TEST 4: Admin Force Cancel")
    
    try:
        # Setup
        setup = create_test_showtime()
        user = create_user(f"admincancel_{time.time()}")
        
        if not user:
            raise Exception("Failed to create user")
        
        # Reserve seat
        log("📍", "Creating reservation...")
        reservation_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=user["headers"],
            json={
                "showtime_id": setup["showtime_id"],
                "seat_code": "R8-8"
            }
        )
        
        if reservation_response.status_code != 200:
            raise Exception(f"Reservation failed: {reservation_response.text}")
        
        reservation_id = reservation_response.json()["id"]
        log("✓", f"Reservation created: {reservation_id}")
        
        # ADMIN FORCE CANCEL
        log("👮", "Admin forcing cancellation...")
        cancel_response = requests.post(
            f"{BASE_URL}/admin/reservations/{reservation_id}/cancel",
            headers=setup["admin"]["headers"]
        )
        
        if cancel_response.status_code != 200:
            raise Exception(f"Admin cancel failed [{cancel_response.status_code}]: {cancel_response.text}")
        
        log("✓", "Admin cancelled reservation")
        
        # Verify reservation cancelled
        reservation_response = requests.get(
            f"{BASE_URL}/reservations/{reservation_id}",
            headers=user["headers"]
        )
        
        if reservation_response.status_code == 200:
            reservation = reservation_response.json()
            if reservation["status"] == "cancelled":
                log("✓", "Reservation correctly cancelled")
            else:
                log("⚠️", f"Reservation status: {reservation['status']}")
        
        test_result("Admin Force Cancel", True)
        return True
        
    except Exception as e:
        log("❌", f"Error: {str(e)}")
        test_result("Admin Force Cancel", False)
        return False

# ============================================================
# TEST 5: CONCURRENT BOOKING (SAME SEAT)
# ============================================================

def test_concurrent_booking():
    log("👥", "TEST 5: Concurrent Booking (Same Seat)")
    
    try:
        # Setup
        setup = create_test_showtime()
        user1 = create_user(f"concurrent1_{time.time()}")
        time.sleep(0.1)  # Small delay to ensure different timestamps
        user2 = create_user(f"concurrent2_{time.time()}")
        
        if not user1 or not user2:
            raise Exception("Failed to create users")
        
        # Both try to reserve same seat
        log("👥", "Two users attempting same seat...")
        response1 = requests.post(
            f"{BASE_URL}/reservations/",
            headers=user1["headers"],
            json={
                "showtime_id": setup["showtime_id"],
                "seat_code": "R9-9"
            }
        )
        
        response2 = requests.post(
            f"{BASE_URL}/reservations/",
            headers=user2["headers"],
            json={
                "showtime_id": setup["showtime_id"],
                "seat_code": "R9-9"
            }
        )
        
        # One should succeed, one should fail
        success_count = sum([
            response1.status_code == 200,
            response2.status_code == 200
        ])
        
        log("ℹ️", f"User 1: {response1.status_code}")
        log("ℹ️", f"User 2: {response2.status_code}")
        
        if success_count != 1:
            raise Exception(f"Expected exactly 1 success, got {success_count}")
        
        log("✓", "Exactly one booking succeeded (correct behavior)")
        
        test_result("Concurrent Booking", True)
        return True
        
    except Exception as e:
        log("❌", f"Error: {str(e)}")
        test_result("Concurrent Booking", False)
        return False

# ============================================================
# MAIN TEST RUNNER
# ============================================================

def main():
    print("\n" + "="*60)
    print("🎬 CINEMA BOOKING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*60 + "\n")
    
    # Run all tests
    test_normal_booking_flow()
    print()
    test_user_cancellation_flow()
    print()
    test_payment_failure_flow()
    print()
    test_admin_force_cancel()
    print()
    test_concurrent_booking()
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📈 Success Rate: {tests_passed}/{tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! YOUR SYSTEM IS FULLY OPERATIONAL! 🎉\n")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Check logs above.\n")

if __name__ == "__main__":
    main()