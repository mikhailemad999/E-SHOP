# E-Shop Marketplace — Audit Report & Remaining Tasks

This document outlines the resolved bugs, current project status, and remaining technical considerations or roadmap items for production readiness.

---

## ✅ Fixed Issues

1. **Authentication API Integration**:
   - **Issue**: `LoginPage.jsx` previously called a local state setter in `authStore.js` rather than sending an HTTP request.
   - **Fix**: Updated `authStore.js` `login()` to send a `POST` request to `/api/auth/login/`, obtain JWT tokens (`access` & `refresh`), and set user state.

2. **Demo Account Credential Mismatch**:
   - **Issue**: Demo login buttons used outdated credentials (`AdminPass123!`, `seller1`) that failed database authentication.
   - **Fix**: Synchronized credentials in `LoginPage.jsx` with `seed_data.py` (`superadmin` / `SuperAdmin123!`, `seller_techworld` / `SellerPass123!`).

3. **Role Specification in Frontend Router**:
   - **Issue**: `App.jsx` checked for `SUPERADMIN` while Django model `User.Role` uses `SUPER_ADMIN`.
   - **Fix**: Updated `ProtectedRoute` role arrays to match backend choice strings (`SUPER_ADMIN`).

4. **Home Page Trending Products**:
   - **Issue**: Home page showed static skeleton loaders without pulling real listings from the API.
   - **Fix**: Connected `HomePage.jsx` to `GET /api/search/`, rendering real product cards dynamically with fallback placeholders.

5. **Cross-Database Full-Text Search Compatibility**:
   - **Issue**: Importing `django.contrib.postgres.search` caused import errors on MySQL environments.
   - **Fix**: Wrapped PostgreSQL search imports conditionally in `views.py` and ensured MySQL uses `icontains` text matching.

---

## ⚠️ Remaining Issues & Enhancements Needed

### 1. Cart Checkout API Integration (High Priority)
* **Current Behavior**: `CartPage.jsx` creates a mock order object in client memory and presents a modal receipt.
* **Impact**: Orders placed in the cart UI are not persisted to the Django `orders` MySQL database table.
* **Suggested Fix**: Update `handleCheckout()` in `CartPage.jsx` to call `POST /api/orders/` with line items, address, and payment choice (`VISA`/`CASH`).

---

### 2. Analytics & Statistics Endpoint
* **Current Behavior**: Calling stats in `AdminDashboard.jsx` yields HTTP 404 because `backend/apps/analytics/urls.py` contains `urlpatterns = []`.
* **Impact**: Admin dashboard metrics display static or dummy charts.
* **Suggested Fix**: Implement Django REST views in `apps/analytics/views.py` to calculate total gross sales, active listing count, and delivery performance, then expose via `analytics/urls.py`.

---

### 3. WebSocket Real-Time Tracking Connection
* **Current Behavior**: `TrackingPage.jsx` uses simulated intervals or polling for order progress updates.
* **Impact**: Real-time WebSocket capabilities configured in `backend/apps/shipping/consumers.py` are not fully connected to the React UI.
* **Suggested Fix**: Instantiate a standard `WebSocket` (`ws://localhost:8000/ws/shipping/<tracking_number>/`) in `TrackingPage.jsx` to receive live location and status updates.

---

### 4. Background Task Queue (Redis / Celery)
* **Current Behavior**: When running outside Docker on a Windows host without Redis on port 6379, async notification tasks emit connection retries.
* **Impact**: Celery tasks (email notifications, payment processing) require Redis to execute asynchronously.
* **Suggested Fix**: Run `docker-compose up redis celery_worker` or set `CELERY_TASK_ALWAYS_EAGER = True` in `config/settings/local.py` for pure offline development.

---

### 5. Custom Media Image Upload Handling
* **Current Behavior**: Seeded products use Unsplash image URLs. Custom seller uploads require local media serving.
* **Impact**: Local image uploads in `POST /api/catalog/listings/` need static URL routing in local Django configuration.
* **Suggested Fix**: Ensure `django.conf.urls.static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` is active in `config/urls.py` during local development.

---

## 🎯 Recommended Next Steps

1. **Implement Cart Checkout endpoint integration** in `frontend/src/pages/customer/CartPage.jsx`.
2. **Build Analytics views** in `backend/apps/analytics/views.py`.
3. **Connect Frontend WebSocket consumer** in `frontend/src/pages/customer/TrackingPage.jsx`.
4. **Push `PROJECT_ISSUES_STATUS.md` to GitHub repository**.
