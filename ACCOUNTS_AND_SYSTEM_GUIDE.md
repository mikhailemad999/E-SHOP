# E-Shop Multi-Vendor Marketplace — Accounts & System Credentials Guide

## System Portals & Service Links

| Service / Dashboard | Direct Access URL | Description |
| :--- | :--- | :--- |
| **Frontend Web App (Customer Home)** | [http://localhost:5173](http://localhost:5173) | Main E-Commerce Web App |
| **Seller Web Dashboard (Add Products)** | [http://localhost:5173/seller/dashboard](http://localhost:5173/seller/dashboard) | Storefront Management & Add Products Live |
| **Delivery Manager Web Dashboard (Add Delivery Boys)** | [http://localhost:5173/delivery/manager](http://localhost:5173/delivery/manager) | Fleet Overview & Register Delivery Boys Live |
| **Delivery Agent Web Dashboard (Update Status & GPS)** | [http://localhost:5173/delivery/agent](http://localhost:5173/delivery/agent) | Package Deliveries & GPS Location Pings |
| **Admin Web Dashboard (Platform Moderation)** | [http://localhost:5173/admin/dashboard](http://localhost:5173/admin/dashboard) | Platform Moderation Queue & Stats |
| **User Login Page (All Roles)** | [http://localhost:5173/login](http://localhost:5173/login) | Unified Login Portal |
| **User Registration Page** | [http://localhost:5173/register](http://localhost:5173/register) | Customer & Seller Sign-up |
| **Django Admin Back-Office** | [http://localhost:8000/admin/](http://localhost:8000/admin/) | Back-office System Admin Panel |
| **Django REST API Base** | [http://localhost:8000/api/](http://localhost:8000/api/) | REST API Root Endpoint |
| **Live Delivery WebSocket Stream** | `ws://localhost:8000/ws/delivery/{tracking_number}/` | Real-time GPS Delivery Tracking Channel |

---

## Active MySQL 5.7 Database Credentials

| Parameter | Connection Value | Direct Link / Tool |
| :--- | :--- | :--- |
| **Database Engine** | MySQL 5.7 / MariaDB (`django.db.backends.mysql`) | MySQL Workbench / phpMyAdmin |
| **Database Name** | `E_shop` | [MySQL Workbench Login](mysql://root:1234@127.0.0.1:3306/E_shop) |
| **Host / IP** | `127.0.0.1` *(or `localhost`)* | `127.0.0.1` |
| **Port** | `3306` | Port 3306 |
| **Database User** | `root` | Root User |
| **Database Password** | `1234` | Password: `1234` |

---

## Direct Clickable Links & User Accounts by Role (All 24 Accounts)

Click on any link below to open the corresponding web dashboard or login portal directly.

### 1. Super Admin Account (1 Account)
> 🔗 **Super Admin Web Dashboard**: [http://localhost:5173/admin/dashboard](http://localhost:5173/admin/dashboard)  
> 🔗 **Django Admin Back-Office**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

| Role | Username | Email | Password | Clickable Direct Web Link |
| :--- | :--- | :--- | :--- | :--- |
| `SUPER_ADMIN` | `superadmin` | `superadmin@eshop.dev` | `SuperAdmin123!` | 👉 [Open Admin Web Dashboard](http://localhost:5173/admin/dashboard) |

---

### 2. Admin Accounts (2 Accounts)
> 🔗 **Admin Web Dashboard**: [http://localhost:5173/admin/dashboard](http://localhost:5173/admin/dashboard)

| Role | Username | Email | Password | Responsibilities | Clickable Direct Web Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ADMIN` | `admin1` | `admin1@eshop.dev` | `AdminPass123!` | Moderation Queue & Approvals | 👉 [Open Admin Web Dashboard](http://localhost:5173/admin/dashboard) |
| `ADMIN` | `admin2` | `admin2@eshop.dev` | `AdminPass123!` | Disputes Resolution & Oversight | 👉 [Open Admin Web Dashboard](http://localhost:5173/admin/dashboard) |

---

### 3. Seller Accounts & Storefronts (5 Shops)
> 🔗 **Seller Web Dashboard (Add Products Live)**: [http://localhost:5173/seller/dashboard](http://localhost:5173/seller/dashboard)

| Role | Shop Name | Username | Seller Email | Password | Primary Inventory | Clickable Direct Web Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SELLER` | **TechWorld Premium** | `seller_techworld` | `techworld@sellers.eshop.dev` | `SellerPass123!` | Laptops, Audio, Cameras | 👉 [Open Seller Dashboard](http://localhost:5173/seller/dashboard) |
| `SELLER` | **Apex Fashion & Co** | `seller_apexfashion` | `apexfashion@sellers.eshop.dev` | `SellerPass123!` | Hoodies, Sneakers, Jackets | 👉 [Open Seller Dashboard](http://localhost:5173/seller/dashboard) |
| `SELLER` | **ChronoLux Timepieces** | `seller_chronolux` | `chronolux@sellers.eshop.dev` | `SellerPass123!` | Swiss Luxury Watches | 👉 [Open Seller Dashboard](http://localhost:5173/seller/dashboard) |
| `SELLER` | **Nest & Haven Decor** | `seller_nesthaven` | `nesthaven@sellers.eshop.dev` | `SellerPass123!` | Coffee Machines, Furniture | 👉 [Open Seller Dashboard](http://localhost:5173/seller/dashboard) |
| `SELLER` | **Pulse Athletics** | `seller_pulseathletics` | `pulse@sellers.eshop.dev` | `SellerPass123!` | Gym Equipment, Dumbbells | 👉 [Open Seller Dashboard](http://localhost:5173/seller/dashboard) |

---

### 4. Delivery Manager Accounts (2 Accounts)
> 🔗 **Delivery Manager Web Dashboard (Add Delivery Boys Live)**: [http://localhost:5173/delivery/manager](http://localhost:5173/delivery/manager)

| Role | Username | Email | Password | Zone | Clickable Direct Web Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DELIVERY_MANAGER` | `manager1` | `manager1@eshop.dev` | `ManagerPass123!` | Zone-1 | 👉 [Open Manager Dashboard](http://localhost:5173/delivery/manager) |
| `DELIVERY_MANAGER` | `manager2` | `manager2@eshop.dev` | `ManagerPass123!` | Zone-2 | 👉 [Open Manager Dashboard](http://localhost:5173/delivery/manager) |

---

### 5. Delivery Agent Accounts (4 Accounts)
> 🔗 **Delivery Agent Web Dashboard (Update Package Status & GPS)**: [http://localhost:5173/delivery/agent](http://localhost:5173/delivery/agent)

| Role | Username | Email | Password | Vehicle | Phone | Clickable Direct Web Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DELIVERY_AGENT` | `agent1_1` | `agent1_1@eshop.dev` | `AgentPass123!` | Motorcycle | `+15550011` | 👉 [Open Agent Dashboard](http://localhost:5173/delivery/agent) |
| `DELIVERY_AGENT` | `agent1_2` | `agent1_2@eshop.dev` | `AgentPass123!` | Car | `+15550012` | 👉 [Open Agent Dashboard](http://localhost:5173/delivery/agent) |
| `DELIVERY_AGENT` | `agent2_1` | `agent2_1@eshop.dev` | `AgentPass123!` | Motorcycle | `+15550021` | 👉 [Open Agent Dashboard](http://localhost:5173/delivery/agent) |
| `DELIVERY_AGENT` | `agent2_2` | `agent2_2@eshop.dev` | `AgentPass123!` | Car | `+15550022` | 👉 [Open Agent Dashboard](http://localhost:5173/delivery/agent) |

---

### 6. Customer (Buyer) Accounts (10 Accounts)
> 🔗 **Customer Login Link**: [http://localhost:5173/login](http://localhost:5173/login)  
> 🔗 **Customer Storefront Link**: [http://localhost:5173](http://localhost:5173)

| Role | Username | Email | Password | Default Address | Clickable Direct Web Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CUSTOMER` | `customer1` | `customer1@eshop.dev` | `CustomerPass123!` | 101 Marketplace Blvd, NY 10001 | 👉 [Login Customer 1](http://localhost:5173/login) |
| `CUSTOMER` | `customer2` | `customer2@eshop.dev` | `CustomerPass123!` | 102 Marketplace Blvd, NY 10001 | 👉 [Login Customer 2](http://localhost:5173/login) |
| `CUSTOMER` | `customer3` ... `customer10` | `customer3@eshop.dev` ... | `CustomerPass123!` | 103-110 Marketplace Blvd, NY 10001 | 👉 [Login Customer](http://localhost:5173/login) |

---

## Quick-Start API Token Command

Authenticate against the backend API to receive JWT tokens:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "CustomerPass123!"}'
```
