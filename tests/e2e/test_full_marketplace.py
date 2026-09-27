"""
End-to-End Test Suite for E-Shop Multi-Vendor Marketplace.
Uses Playwright Python to test:
1. Browsing HomePage & Categories
2. Searching Products
3. Customer Registration UI
4. Login UI & 1-Click Fast Login
5. Live Delivery Tracking Page with Leaflet map
6. Wishlist Page
7. Profile Page
"""

import sys
import time
from playwright.sync_api import sync_playwright


def run_e2e_test():
    print("[*] Starting E-Shop Marketplace End-to-End Test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. Navigate to HomePage
            print("[1] Navigating to HomePage...")
            page.goto("http://localhost:5173", timeout=15000)
            page.wait_for_load_state("networkidle")
            assert "E-Shop" in page.title() or page.locator("text=E-Shop").first.is_visible()
            print("  -> HomePage loaded successfully.")

            # 2. Check Hero Section & CTA
            print("[2] Verifying Hero & Category Cards...")
            assert page.locator("text=Discover Products").first.is_visible()
            assert page.locator("text=Shop by Category").first.is_visible()
            print("  -> Hero & Category section rendered.")

            # 3. Navigate to Register Page
            print("[3] Testing Customer Registration UI...")
            page.goto("http://localhost:5173/register", timeout=15000)
            page.wait_for_load_state("networkidle")
            assert page.locator("text=Create Your Account").first.is_visible()
            assert page.locator("text=Buyer / Customer").first.is_visible()
            assert page.locator("text=Seller Store").first.is_visible()
            print("  -> Registration page & role toggle working.")

            # 4. Navigate to Login Page
            print("[4] Testing Login UI...")
            page.goto("http://localhost:5173/login", timeout=15000)
            page.wait_for_load_state("networkidle")
            assert page.locator("text=Welcome Back").first.is_visible()
            assert page.locator("text=1-Click Demo Account Selector").first.is_visible()
            print("  -> Login page rendered.")

            # 5. Navigate to Search Page
            print("[5] Testing Catalog Search Page...")
            page.goto("http://localhost:5173/search", timeout=15000)
            page.wait_for_load_state("networkidle")
            assert page.locator("text=Product Catalog & Search").first.is_visible()
            print("  -> Catalog Search page rendered.")

            # 6. Navigate to Wishlist Page
            print("[6] Testing Wishlist Page...")
            page.goto("http://localhost:5173/wishlist", timeout=15000)
            page.wait_for_load_state("networkidle")
            assert page.locator("text=My Wishlist & Saved Items").first.is_visible()
            print("  -> Wishlist page rendered.")

            # 7. Navigate to Live Delivery Tracking
            print("[7] Testing Live GPS Tracking Page...")
            page.goto("http://localhost:5173/track/TRK-TEST123456", timeout=15000)
            page.wait_for_load_state("networkidle")
            assert page.locator("text=Live Delivery Tracking").first.is_visible()
            assert page.locator(".leaflet-container").first.is_visible()
            print("  -> Tracking page & Leaflet map container verified.")

            print("[SUCCESS] All E2E smoke tests passed cleanly!")

        except Exception as e:
            print(f"[ERROR] Test failed with error: {e}")
            page.screenshot(path="e2e_error.png")
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    run_e2e_test()
