"""
Django Management Command: Seed 100+ Products, Categories, Shops, and All 6 User Roles.
Usage: python manage.py seed_data
"""

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.accounts.models import Address, DeliveryAgentProfile, DeliveryManagerProfile, SellerProfile, User
from apps.catalog.models import Category, Listing, Product, ProductImage, Shop

CATEGORIES_DATA = [
    {
        "name": "Electronics",
        "slug": "electronics",
        "sub": ["Laptops", "Audio & Headphones", "Cameras", "Gaming Consoles", "Monitors & Accessories"],
    },
    {
        "name": "Smartphones & Tablets",
        "slug": "smartphones",
        "sub": ["Smartphones", "Tablets", "Cases & Protection", "Wearable Tech", "Chargers & Cables"],
    },
    {
        "name": "Fashion & Apparel",
        "slug": "fashion",
        "sub": ["Men's Wear", "Women's Wear", "Footwear & Sneakers", "Bags & Luggage", "Accessories"],
    },
    {
        "name": "Luxury Watches",
        "slug": "watches",
        "sub": ["Automatic Watches", "Chronographs", "Smartwatches", "Vintage Watches"],
    },
    {
        "name": "Home & Living",
        "slug": "home-living",
        "sub": ["Kitchen Appliances", "Furniture", "Bedding & Bath", "Lighting & Decor", "Smart Home"],
    },
    {
        "name": "Sports & Fitness",
        "slug": "sports",
        "sub": ["Gym Equipment", "Outdoor Gear", "Bicycles", "Fitness Apparel"],
    },
    {
        "name": "Beauty & Personal Care",
        "slug": "beauty",
        "sub": ["Skincare", "Fragrances", "Haircare", "Grooming Tools"],
    },
]

SHOPS_DATA = [
    {
        "name": "TechWorld Premium",
        "username": "seller_techworld",
        "email": "techworld@sellers.eshop.dev",
        "description": "Authorized dealer for high-end electronics, laptops, and gadgets.",
    },
    {
        "name": "Apex Fashion & Co",
        "username": "seller_apexfashion",
        "email": "apexfashion@sellers.eshop.dev",
        "description": "Trendy apparel, streetwear, sneakers, and designer accessories.",
    },
    {
        "name": "ChronoLux Timepieces",
        "username": "seller_chronolux",
        "email": "chronolux@sellers.eshop.dev",
        "description": "Swiss luxury watches, chronographs, and collector timepieces.",
    },
    {
        "name": "Nest & Haven Decor",
        "username": "seller_nesthaven",
        "email": "nesthaven@sellers.eshop.dev",
        "description": "Modern home furniture, smart appliances, and interior decor.",
    },
    {
        "name": "Pulse Athletics",
        "username": "seller_pulseathletics",
        "email": "pulse@sellers.eshop.dev",
        "description": "Professional fitness gear, gym equipment, and performance apparel.",
    },
]

BASE_PRODUCTS = [
    # Electronics (15 items)
    ("MacBook Pro 16 M3 Max", "Electronics", "Apple", 2499.00, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800"),
    ("Dell XPS 15 OLED Touch", "Electronics", "Dell", 1899.00, "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800"),
    ("Sony WH-1000XM5 Noise Canceling Headphones", "Electronics", "Sony", 399.00, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"),
    ("Bose QuietComfort Ultra Headphones", "Electronics", "Bose", 429.00, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800"),
    ("Logitech MX Master 3S Ergonomic Mouse", "Electronics", "Logitech", 99.00, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800"),
    ("Asus ROG Strix Gaming Laptop 18", "Electronics", "Asus", 2199.00, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800"),
    ("Keychron Q1 Pro Wireless Mechanical Keyboard", "Electronics", "Keychron", 199.00, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800"),
    ("Samsung Odyssey G9 49 Curved Gaming Monitor", "Electronics", "Samsung", 1299.00, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800"),
    ("Canon EOS R5 Mirrorless Camera Body", "Electronics", "Canon", 3899.00, "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"),
    ("Sony Alpha A7 IV Full Frame Camera", "Electronics", "Sony", 2498.00, "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800"),
    ("DJI Mini 4 Pro Fly More Combo Drone", "Electronics", "DJI", 1099.00, "https://images.unsplash.com/photo-1527977966376-1c8408f9f108?w=800"),
    ("PlayStation 5 Console Digital Edition", "Electronics", "Sony", 449.00, "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800"),
    ("Xbox Series X 1TB Gaming Console", "Electronics", "Microsoft", 499.00, "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=800"),
    ("Nintendo Switch OLED Model White", "Electronics", "Nintendo", 349.00, "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=800"),
    ("Sennheiser HD 660S2 Open Back Headphones", "Electronics", "Sennheiser", 599.00, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800"),

    # Smartphones & Tablets (15 items)
    ("iPhone 15 Pro Max 256GB Titanium", "Smartphones & Tablets", "Apple", 1199.00, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800"),
    ("Samsung Galaxy S24 Ultra 512GB", "Smartphones & Tablets", "Samsung", 1299.00, "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800"),
    ("Google Pixel 8 Pro 128GB Bay Blue", "Smartphones & Tablets", "Google", 999.00, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800"),
    ("iPad Pro 12.9 Inch M2 Chip 256GB", "Smartphones & Tablets", "Apple", 1099.00, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800"),
    ("Samsung Galaxy Tab S9 Ultra 14.6 Inch", "Smartphones & Tablets", "Samsung", 1199.00, "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800"),
    ("Apple Watch Ultra 2 Titanium Case", "Smartphones & Tablets", "Apple", 799.00, "https://images.unsplash.com/photo-1510017803434-a899398421b3?w=800"),
    ("Anker 737 Power Bank 24000mAh 140W", "Smartphones & Tablets", "Anker", 149.00, "https://images.unsplash.com/photo-1609592424074-b525d8869c9b?w=800"),
    ("MagSafe Wireless Fast Charger 15W", "Smartphones & Tablets", "Apple", 39.00, "https://images.unsplash.com/photo-1622445268465-8438165a2683?w=800"),
    ("OnePlus 12 512GB Emerald Green", "Smartphones & Tablets", "OnePlus", 799.00, "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800"),
    ("iPad Air 11 Inch M2 128GB", "Smartphones & Tablets", "Apple", 599.00, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800"),
    ("Xiaomi 14 Ultra 512GB Camera Phone", "Smartphones & Tablets", "Xiaomi", 1199.00, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800"),
    ("Samsung Galaxy Z Fold 5 512GB", "Smartphones & Tablets", "Samsung", 1799.00, "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800"),
    ("Garmin Epix Pro Gen 2 Sapphire 47mm", "Smartphones & Tablets", "Garmin", 999.00, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800"),
    ("AirPods Pro 2nd Gen USB-C", "Smartphones & Tablets", "Apple", 249.00, "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800"),
    ("Sony WF-1000XM5 Wireless Earbuds", "Smartphones & Tablets", "Sony", 299.00, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800"),

    # Fashion (15 items)
    ("Minimalist Oversized Cotton Fleece Hoodie", "Fashion & Apparel", "Apex", 85.00, "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800"),
    ("Classic Raw Denim Jacket Indigo", "Fashion & Apparel", "Levi's", 120.00, "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800"),
    ("Handcrafted Leather Chelsea Boots", "Fashion & Apparel", "Apex", 210.00, "https://images.unsplash.com/photo-1638247025967-b4e38f787b76?w=800"),
    ("Nike Air Force 1 07 Triple White", "Fashion & Apparel", "Nike", 115.00, "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800"),
    ("Adidas Ultraboost Light Running Shoes", "Fashion & Apparel", "Adidas", 190.00, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800"),
    ("Italian Calfskin Leather Crossbody Bag", "Fashion & Apparel", "Apex", 295.00, "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800"),
    ("Mongolian Cashmere Crewneck Sweater", "Fashion & Apparel", "Apex", 185.00, "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800"),
    ("Tailored Slim-Fit Wool Blazer Navy", "Fashion & Apparel", "Apex", 340.00, "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800"),
    ("Jordan 1 Retro High OG Chicago", "Fashion & Apparel", "Nike", 220.00, "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800"),
    ("New Balance 990v6 Made in USA", "Fashion & Apparel", "New Balance", 200.00, "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800"),
    ("Vintage Leather Biker Motorcycle Jacket", "Fashion & Apparel", "Apex", 450.00, "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800"),
    ("Waterproof Technical Parka Jacket", "Fashion & Apparel", "Apex", 280.00, "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=800"),
    ("Classic Aviator Polarized Sunglasses", "Fashion & Apparel", "Ray-Ban", 165.00, "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800"),
    ("Merino Wool Beanie Hat Slate", "Fashion & Apparel", "Apex", 45.00, "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=800"),
    ("Full Grain Leather Travel Duffle Bag", "Fashion & Apparel", "Apex", 350.00, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800"),

    # Luxury Watches (10 items)
    ("ChronoLux Grand Heritage Automatic 41mm", "Luxury Watches", "ChronoLux", 3450.00, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"),
    ("Seiko Prospex Automatic Diver 200m", "Luxury Watches", "Seiko", 475.00, "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800"),
    ("Tissot PRX Powermatic 80 Blue Dial", "Luxury Watches", "Tissot", 675.00, "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800"),
    ("Tag Heuer Carrera Chronograph Automatic", "Luxury Watches", "Tag Heuer", 5200.00, "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800"),
    ("Hamilton Khaki Field Mechanical 38mm", "Luxury Watches", "Hamilton", 550.00, "https://images.unsplash.com/photo-1614164185128-e4ec99c436d7?w=800"),
    ("Garmin Fenix 7 Pro Sapphire Solar GPS", "Luxury Watches", "Garmin", 899.00, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800"),
    ("Omega Speedmaster Professional Moonwatch", "Luxury Watches", "Omega", 7600.00, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"),
    ("Rolex Submariner Date Oystersteel 41mm", "Luxury Watches", "Rolex", 10250.00, "https://images.unsplash.com/photo-1548690312-e3b507d8c110?w=800"),
    ("Tudor Black Bay Fifty-Eight Black", "Luxury Watches", "Tudor", 3950.00, "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800"),
    ("Casio G-Shock GA-B2100 Octagon Bluetooth", "Luxury Watches", "Casio", 150.00, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800"),

    # Home & Living (10 items)
    ("Espresso Express Pro Commercial Machine", "Home & Living", "Nest Haven", 699.00, "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=800"),
    ("Dyson V15 Detect Cordless Vacuum Cleaner", "Home & Living", "Dyson", 749.00, "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800"),
    ("Philips Airfryer XXL Smart Sensing", "Home & Living", "Philips", 299.00, "https://images.unsplash.com/photo-1585515320310-259814833e62?w=800"),
    ("Modern Scandinavian Walnut Lounge Chair", "Home & Living", "Nest Haven", 450.00, "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=800"),
    ("Ceramic Non-Stick Cookware Set 10 Piece", "Home & Living", "Nest Haven", 220.00, "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=800"),
    ("Smart LED Ambience Light Bar Set 2pk", "Home & Living", "Philips", 129.00, "https://images.unsplash.com/photo-1550985616-10810253b84d?w=800"),
    ("KitchenAid Artisan Stand Mixer 5 Quart", "Home & Living", "KitchenAid", 449.00, "https://images.unsplash.com/photo-1594385208974-2e75f8d7bb48?w=800"),
    ("iRobot Roomba j7+ Self-Emptying Robot", "Home & Living", "iRobot", 799.00, "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800"),
    ("Egyptian Cotton 1000 Thread Sheet Set", "Home & Living", "Nest Haven", 160.00, "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=800"),
    ("Handcrafted Ceramic Table Lamp Warm White", "Home & Living", "Nest Haven", 135.00, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800"),

    # Sports & Fitness (10 items)
    ("Pulse Pro Adjustable Dumbbell Set 50lbs", "Sports & Fitness", "Pulse", 349.00, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800"),
    ("Foldable Motorized Treadmill Heart Rate Monitor", "Sports & Fitness", "Pulse", 799.00, "https://images.unsplash.com/photo-1576678927484-cc909957088c?w=800"),
    ("Carbon Fiber Mountain Bike 29 Inch Wheels", "Sports & Fitness", "Pulse", 1499.00, "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800"),
    ("High-Density Eco Yoga Mat 6mm Cushion", "Sports & Fitness", "Pulse", 45.00, "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=800"),
    ("Concept2 Ergometer Rower Model D", "Sports & Fitness", "Concept2", 990.00, "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800"),
    ("Bowflex SelectTech 552 Adjustable Dumbbells", "Sports & Fitness", "Bowflex", 429.00, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800"),
    ("Thule Chasm Waterproof Duffel Bag 70L", "Sports & Fitness", "Thule", 160.00, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800"),
    ("Garmin HRM-Pro Plus Chest Strap Monitor", "Sports & Fitness", "Garmin", 129.00, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800"),
    ("Hydro Flask 32oz Wide Mouth Water Bottle", "Sports & Fitness", "Hydro Flask", 45.00, "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800"),
    ("Peloton Bike+ Interactive Exercise Bike", "Sports & Fitness", "Peloton", 2495.00, "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800"),

    # Beauty & Personal Care (10 items)
    ("Hydrating Botanical Facial Serum 50ml", "Beauty & Personal Care", "GlowLab", 68.00, "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800"),
    ("Luxury Artisanal Eau de Parfum 100ml", "Beauty & Personal Care", "Maison", 185.00, "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800"),
    ("Sonic Deep Cleansing Facial Brush Tool", "Beauty & Personal Care", "GlowLab", 110.00, "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800"),
    ("Advanced Repair Night Serum Complex", "Beauty & Personal Care", "GlowLab", 95.00, "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800"),
    ("Dyson Supersonic Ionic Hair Dryer", "Beauty & Personal Care", "Dyson", 429.00, "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800"),
    ("Organic Argan Oil Hair Treatment 100ml", "Beauty & Personal Care", "GlowLab", 38.00, "https://images.unsplash.com/photo-1608248597261-e4d0947c6b1e?w=800"),
    ("Philips Sonicare DiamondClean Electric Toothbrush", "Beauty & Personal Care", "Philips", 199.00, "https://images.unsplash.com/photo-1559591937-e68fb3305e43?w=800"),
    ("Chanel Bleu de Chanel Eau de Parfum", "Beauty & Personal Care", "Chanel", 155.00, "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800"),
    ("Retinol 1% Regenerating Night Cream", "Beauty & Personal Care", "GlowLab", 54.00, "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800"),
    ("Mineral Sunscreen Broad Spectrum SPF 50", "Beauty & Personal Care", "GlowLab", 34.00, "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800"),
]


class Command(BaseCommand):
    help = "Seed database with 100+ product listings, categories, shops, and all 6 user roles."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("[SEED] Starting Database Seeding Process..."))

        # 1. Create Roles & Users
        self.stdout.write("1. Creating User Accounts...")

        # Super Admin
        super_admin, _ = User.objects.get_or_create(
            email="superadmin@eshop.dev",
            defaults={
                "username": "superadmin",
                "first_name": "Super",
                "last_name": "Admin",
                "role": User.Role.SUPER_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        super_admin.set_password("SuperAdmin123!")
        super_admin.save()

        # Admins
        for i in range(1, 3):
            u, _ = User.objects.get_or_create(
                email=f"admin{i}@eshop.dev",
                defaults={
                    "username": f"admin{i}",
                    "first_name": "System",
                    "last_name": f"Admin {i}",
                    "role": User.Role.ADMIN,
                    "is_staff": True,
                },
            )
            u.set_password("AdminPass123!")
            u.save()

        # Delivery Managers
        for i in range(1, 3):
            u, _ = User.objects.get_or_create(
                email=f"manager{i}@eshop.dev",
                defaults={
                    "username": f"manager{i}",
                    "first_name": "Delivery",
                    "last_name": f"Manager {i}",
                    "role": User.Role.DELIVERY_MANAGER,
                },
            )
            u.set_password("ManagerPass123!")
            u.save()
            DeliveryManagerProfile.objects.get_or_create(user=u, defaults={"zone": f"Zone-{i}"})

            # Delivery Agents per manager
            for j in range(1, 3):
                agent, _ = User.objects.get_or_create(
                    email=f"agent{i}_{j}@eshop.dev",
                    defaults={
                        "username": f"agent{i}_{j}",
                        "first_name": "Agent",
                        "last_name": f"{i}-{j}",
                        "role": User.Role.DELIVERY_AGENT,
                        "phone": f"+155500{i}{j}",
                    },
                )
                agent.set_password("AgentPass123!")
                agent.save()
                DeliveryAgentProfile.objects.get_or_create(
                    user=agent,
                    defaults={
                        "delivery_manager": u,
                        "vehicle_type": "motorcycle" if j == 1 else "car",
                        "license_plate": f"PLATE-{i}{j}9",
                    },
                )

        # Customers
        customers = []
        for i in range(1, 11):
            c, _ = User.objects.get_or_create(
                email=f"customer{i}@eshop.dev",
                defaults={
                    "username": f"customer{i}",
                    "first_name": "Customer",
                    "last_name": str(i),
                    "role": User.Role.CUSTOMER,
                    "phone": f"+1800555{i:04d}",
                },
            )
            c.set_password("CustomerPass123!")
            c.save()
            Address.objects.get_or_create(
                user=c,
                label="Home",
                defaults={
                    "full_name": f"Customer {i} Test",
                    "phone": c.phone,
                    "address_line1": f"{100 + i} Marketplace Blvd",
                    "city": "New York",
                    "state": "NY",
                    "postal_code": "10001",
                    "country": "US",
                    "is_default": True,
                },
            )
            customers.append(c)

        # Sellers & Shops
        shops = []
        for shop_info in SHOPS_DATA:
            seller, _ = User.objects.get_or_create(
                email=shop_info["email"],
                defaults={
                    "username": shop_info["username"],
                    "first_name": shop_info["name"].split()[0],
                    "last_name": "Seller",
                    "role": User.Role.SELLER,
                },
            )
            seller.set_password("SellerPass123!")
            seller.save()
            SellerProfile.objects.get_or_create(user=seller, defaults={"business_name": shop_info["name"]})

            shop, _ = Shop.objects.get_or_create(
                owner=seller,
                defaults={
                    "name": shop_info["name"],
                    "slug": slugify(shop_info["name"]),
                    "description": shop_info["description"],
                    "rating": Decimal(str(round(random.uniform(4.2, 4.9), 2))),
                    "total_sales": random.randint(50, 500),
                },
            )
            shops.append(shop)

        # 2. Categories
        self.stdout.write("2. Creating Categories...")
        cat_map = {}
        for c_data in CATEGORIES_DATA:
            parent_cat, _ = Category.objects.get_or_create(
                slug=c_data["slug"],
                defaults={"name": c_data["name"]},
            )
            cat_map[c_data["name"]] = parent_cat
            for sub_name in c_data["sub"]:
                sub_cat, _ = Category.objects.get_or_create(
                    slug=slugify(sub_name),
                    defaults={"name": sub_name, "parent": parent_cat},
                )

        # 3. Create 100+ Products & Listings
        self.stdout.write("3. Seeding 100+ Products & Multi-Seller Listings...")
        total_created = 0

        for title, cat_name, brand, base_price, img_url in BASE_PRODUCTS:
            parent_category = cat_map.get(cat_name)
            prod_slug = slugify(title)

            product, _ = Product.objects.get_or_create(
                slug=prod_slug,
                defaults={
                    "title": title,
                    "category": parent_category,
                    "brand": brand,
                    "description": f"High quality {title}. Designed and engineered to exceed expectations with premium materials and finish.",
                    "base_attributes": {"brand": brand, "category": cat_name},
                },
            )

            # Assign 1-2 sellers per product to demonstrate Buy-Box price competition
            assigned_shops = random.sample(shops, k=random.randint(1, 2))
            for idx, shop in enumerate(assigned_shops):
                price_variation = Decimal(str(round(base_price * random.uniform(0.96, 1.06), 2)))
                stock = random.randint(10, 80)

                listing, created = Listing.objects.get_or_create(
                    product=product,
                    shop=shop,
                    defaults={
                        "price": price_variation,
                        "compare_at_price": Decimal(str(round(price_variation * Decimal("1.25"), 2))),
                        "stock_qty": stock,
                        "condition": Listing.Condition.NEW if idx == 0 else Listing.Condition.REFURBISHED,
                        "status": Listing.Status.LIVE,
                        "sku": f"SKU-{product.id}-{shop.id}",
                        "rating": Decimal(str(round(random.uniform(4.1, 5.0), 2))),
                        "review_count": random.randint(8, 150),
                    },
                )

                if created:
                    ProductImage.objects.create(
                        listing=listing,
                        image=img_url,
                        alt_text=title,
                        sort_order=0,
                    )
                    total_created += 1

        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Successfully seeded {total_created} Product Listings across {len(shops)} Shops!"))
        self.stdout.write(self.style.SUCCESS("[ACCOUNT] Super Admin: superadmin@eshop.dev / SuperAdmin123!"))
        self.stdout.write(self.style.SUCCESS("[ACCOUNT] Seller: techworld@sellers.eshop.dev / SellerPass123!"))
        self.stdout.write(self.style.SUCCESS("[ACCOUNT] Customer: customer1@eshop.dev / CustomerPass123!"))
