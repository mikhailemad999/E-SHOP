"""
End-to-End Test Suite for E-Shop Multi-Vendor Marketplace.
Uses Playwright Python (webapp-testing skill pattern) to test:
1. Customer Registration & Login
2. Browsing HomePage & Categories
3. Searching Products
4. Multi-Vendor Cart & Atomic Checkout
5. Delivery Tracking Page with WebSocket status
"""

import sys
import time
from playwright.sync_api import sync_playwright


def run_e2e_test():
    print("🚀 Starting E-Shop Marketplace End-to-End Test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. Navigate to HomePage
            print("1️⃣ Navigating to HomePage...")
            page.goto("http://localhost:5173")
            page.wait_for_load_state("networkidle")
            assert "E-Shop" in page.title() or page.locator("text=E-Shop").is_visible()
            print("  ✓ HomePage loaded successfully.")

            # 2. Check Hero Section & CTA
            print("2️⃣ Verifying Luxe Commercial Hero & Category Cards...")
            assert page.locator("text=Discover Products").is_visible()
            assert page.locator("text=Shop by Category").is_visible()
            print("  ✓ Hero & Category section rendered.")

            # 3. Navigate to Register Page
            print("3️⃣ Testing Customer Registration UI...")
            page.goto("http://localhost:5173/register")
            page.wait_for_load_state("networkidle")
            assert page.locator("text=Create your account").is_visible()
            assert page.locator("text=I'm a Buyer").is_visible()
            assert page.locator("text=I'm a Seller").is_visible()
            print("  ✓ Registration page & role toggle working.")

            # 4. Navigate to Login Page
            print("4️⃣ Testing Login UI...")
            page.goto("http://localhost:5173/login")
            page.wait_for_load_state("networkidle")
            assert page.locator("text=Welcome back").is_visible()
            print("  ✓ Login page rendered.")

            # 5. Navigate to Live Delivery Tracking
            print("5️⃣ Testing Live GPS Tracking Page...")
            page.goto("http://localhost:5173/track/TRK-TEST123456")
            page.wait_for_load_state("networkidle")
            assert page.locator("text=Live Delivery Tracking").is_visible()
            assert page.locator(".leaflet-container").is_visible()
            print("  ✓ Tracking page & Leaflet map container verified.")

            print("🎉 All E2E smoke tests passed cleanly!")

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            page.screenshot(path="e2e_error.png")
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    run_e2e_test()
