# 🛒 E-Shop — Enterprise Multi-Vendor Marketplace Platform

[![React](https://img.shields.io/badge/React-18-blue.svg?logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg?logo=vite)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20.svg?logo=django)](https://www.djangoproject.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?logo=mysql)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, multi-vendor e-commerce marketplace platform built with **Django REST Framework** (Python), **React + Vite** (JavaScript/Zustand), **MySQL**, **JWT Authentication**, and **Real-Time WebSocket Order Tracking**.

---

## 🌟 Key Features

### 🛍️ Customer Experience
- **Luxe Commercial Aesthetic**: Modern responsive UI engineered with high-contrast typography and subtle glassmorphic micro-interactions.
- **Faceted Product Search & Filtering**: Real-time keyword search, multi-category tree selection, min/max price range sliders, quick price preset chips, and sorting controls.
- **Multi-Vendor Buy-Box**: Canonical product catalog with multi-seller listings and live stock auto-deduction.
- **Persistent Shopping Cart & Checkout**: Integrated checkout API supporting VISA/Credit Card and Cash on Delivery (COD) with printable order receipts.
- **Real-Time Order Tracking**: Live GPS marker updates via WebSocket with automatic HTTP polling fallback.

---

### 🏪 Seller Storefront & Operations
- **Storefront Management**: Dedicated seller control panel (`/seller`) for listing products, managing inventory, and viewing incoming customer orders.
- **Automated Stock Deduction**: Inventory auto-deducts atomically upon order confirmation.
- **Sales Analytics**: Real-time sales revenue reports, units sold, and printable receipts.

---

### 🚚 Logistics & Fleet Management
- **Delivery Manager Dashboard** (`/delivery`): Fleet assignment, zone-based dispatcher overview, and delivery status monitoring.
- **Delivery Agent Portal** (`/delivery/agent`): Dispatch list, interactive route map, and delivery status pings.

---

### 🛡️ Back-Office & Administration
- **Admin Control Center** (`/admin`): Real-time platform metrics (total users, live listings, pending review count, gross sales) connected live to MySQL `/api/stats/`.
- **Listing Moderation Queue**: Approve or reject seller offers prior to catalog publication.
- **Django Admin Interface**: Native administrative backend at `http://localhost:8000/admin/`.

---

### 🔑 Security & Authentication
- **Role-Based Access Control (RBAC)**: Supports 6 distinct roles: `Customer`, `Seller`, `Delivery Agent`, `Delivery Manager`, `Admin`, `Super Admin`.
- **Universal Multi-Role Registration**: Self-registration portal (`/register`) supporting instant signup for all 6 account roles.
- **Automatic Role Navigation**: Logins (`/login`) automatically inspect user database roles and route users straight to their respective dashboard.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend Framework** | React 18, Vite, React Router v7, Zustand (State Management), Axios |
| **Styling & UI** | Vanilla CSS Design Tokens, Lucide Icons, Leaflet / OpenStreetMap |
| **Backend API** | Python 3.12, Django 5.0, Django REST Framework, Django Channels (WebSockets) |
| **Database & Cache** | MySQL 8.0, Redis (Celery Tasks & WebSockets), LocMem Cache |
| **Authentication** | Simple JWT (Bearer Access & Refresh Tokens), CORS Headers |
| **Containerization** | Docker, Docker Compose |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & npm
- **MySQL 8.0+** running locally on port 3306

---

### 1. Backend Installation (Django REST API)

```bash
# Navigate to backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements/local.txt

# Execute database migrations
python manage.py migrate --settings=config.settings.local

# Seed initial database (100+ listings, categories, shops, and demo accounts)
python manage.py seed_data --settings=config.settings.local

# Start Django backend server
python manage.py runserver 8000 --settings=config.settings.local
```

The REST API will start at: `http://localhost:8000/api/`

---

### 2. Frontend Installation (React + Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server
npm run dev
```

The web application will open at: `http://localhost:5173/`

---

## 🔑 Demo Account Credentials

The database includes pre-seeded demo accounts for testing every role directly on the **1-Click Demo Login Bar** on [`/login`](http://localhost:5173/login):

| Role | Username / Email | Password | Dedicated Route |
| :--- | :--- | :--- | :--- |
| 👑 **Super Admin** | `superadmin` / `superadmin@eshop.dev` | `SuperAdmin123!` | [`http://localhost:5173/admin`](http://localhost:5173/admin) |
| 🛡️ **System Admin** | `admin1` / `admin1@eshop.dev` | `AdminPass123!` | [`http://localhost:5173/admin`](http://localhost:5173/admin) |
| 🏪 **Seller (TechWorld)** | `seller_techworld` / `techworld@sellers.eshop.dev` | `SellerPass123!` | [`http://localhost:5173/seller`](http://localhost:5173/seller) |
| 🚚 **Delivery Manager** | `manager1` / `manager1@eshop.dev` | `ManagerPass123!` | [`http://localhost:5173/delivery`](http://localhost:5173/delivery) |
| 🛵 **Delivery Agent** | `agent1_1` / `agent1_1@eshop.dev` | `AgentPass123!` | [`http://localhost:5173/delivery/agent`](http://localhost:5173/delivery/agent) |
| 🛍️ **Customer** | `customer1` / `customer1@eshop.dev` | `CustomerPass123!` | [`http://localhost:5173/`](http://localhost:5173/) |

---

## 📁 Project Architecture

```
E-SHOP/
├── backend/                  # Django 5.0 REST Framework & Channels API
│   ├── apps/
│   │   ├── accounts/         # User roles, profiles (Seller, Delivery, Address), auth URLs
│   │   ├── analytics/        # Platform stats API (/api/stats/) and audit logging
│   │   ├── catalog/          # Products, multi-seller listings, categories, search API
│   │   ├── orders/           # Shopping cart, multi-vendor order splitting checkout API
│   │   ├── shipping/         # Delivery dispatch, tracking consumer, WS routing
│   │   ├── payments/         # Payment integration choices (VISA, Cash on Delivery)
│   │   └── reviews/          # Ratings, reviews, and favorite listings
│   ├── config/               # Environment settings (local, production), ASGI, WSGI, URLs
│   └── manage.py
├── frontend/                 # React 18 + Vite SPA
│   ├── src/
│   │   ├── api/              # Axios client with automatic JWT refresh interceptors
│   │   ├── components/       # Atomic UI components (atoms, molecules, organisms)
│   │   ├── layouts/          # Main customer layout with clean navbar & footer
│   │   ├── pages/            # Domain views (customer, seller, delivery, admin, auth)
│   │   ├── stores/           # Zustand state management (authStore, cartStore)
│   │   └── App.jsx           # Protected routes and role-aware router
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml        # Docker orchestrator
└── README.md
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
