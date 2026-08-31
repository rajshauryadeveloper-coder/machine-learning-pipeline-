import logging
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.database import get_connection
from src.db.schema import reset_schema

logger = logging.getLogger(__name__)

# Realistic Seed Data Definitions
CATEGORIES_DATA = [
    {
        "name": "Consumer Electronics",
        "slug": "consumer-electronics",
        "description": "Smartphones, tablets, headphones, and audio devices.",
        "is_active": True,
    },
    {
        "name": "Computers & Laptops",
        "slug": "computers-and-laptops",
        "description": "Workstations, ultrabooks, monitors, and components.",
        "is_active": True,
    },
    {
        "name": "Home & Kitchen",
        "slug": "home-and-kitchen",
        "description": "Smart appliances, cookware, and furniture essentials.",
        "is_active": True,
    },
    {
        "name": "Books & Audiobooks",
        "slug": "books-and-audiobooks",
        "description": "Bestsellers, technical guides, and non-fiction titles.",
        "is_active": True,
    },
    {
        "name": "Apparel & Footwear",
        "slug": "apparel-and-footwear",
        "description": "Men and women fashion, athletic wear, and footwear.",
        "is_active": True,
    },
    {
        "name": "Sports & Fitness",
        "slug": "sports-and-fitness",
        "description": "Gym equipment, outdoor gear, and athletic accessories.",
        "is_active": True,
    },
    {
        "name": "Beauty & Personal Care",
        "slug": "beauty-and-personal-care",
        "description": "Skincare serums, organic cosmetics, and grooming kits.",
        "is_active": True,
    },
    {
        "name": "Toys & Board Games",
        "slug": "toys-and-board-games",
        "description": "STEM learning toys, strategy games, and collectibles.",
        "is_active": True,
    },
    {
        "name": "Automotive & Tools",
        "slug": "automotive-and-tools",
        "description": "Diagnostic tools, detailing supplies, and hardware.",
        "is_active": True,
    },
    {
        "name": "Health & Nutrition",
        "slug": "health-and-nutrition",
        "description": "Vitamins, clean protein, and wellness supplements.",
        "is_active": True,
    },
]

FIRST_NAMES = [
    "Alex",
    "Emma",
    "Liam",
    "Sophia",
    "Noah",
    "Olivia",
    "Ethan",
    "Ava",
    "Mason",
    "Isabella",
    "Lucas",
    "Mia",
    "Oliver",
    "Harper",
    "Elijah",
    "Evelyn",
    "Aiden",
    "Abigail",
    "James",
    "Emily",
    "Benjamin",
    "Ella",
    "Sebastian",
    "Aria",
    "Henry",
    "Scarlett",
    "Alexander",
    "Grace",
    "Jackson",
    "Chloe",
    "Daniel",
    "Camila",
    "Matthew",
    "Penelope",
    "Samuel",
    "Riley",
    "David",
    "Layla",
    "Joseph",
    "Zoey",
]

LAST_NAMES = [
    "Johnson",
    "Smith",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
    "Harris",
    "Sanchez",
    "Clark",
    "Ramirez",
    "Lewis",
    "Robinson",
    "Walker",
    "Young",
    "Allen",
    "King",
    "Wright",
    "Scott",
    "Torres",
    "Nguyen",
    "Hill",
    "Flores",
]

CITIES = [
    "New York",
    "San Francisco",
    "Austin",
    "Seattle",
    "Chicago",
    "Boston",
    "Denver",
    "Los Angeles",
    "Portland",
    "Miami",
    "San Diego",
    "Atlanta",
    "Dallas",
    "Phoenix",
    "Philadelphia",
    "Nashville",
    "Minneapolis",
    "Raleigh",
]

PRODUCTS_SEED = [
    (
        "Quantum Pro Noise-Cancelling Headphones",
        "ELE-HP-001",
        1,
        "299.99",
        85,
        4.85,
        "High-fidelity active noise cancellation with 40-hour battery life.",
    ),
    (
        "PixelView 27-inch 4K UHD Monitor",
        "CMP-MN-002",
        2,
        "449.50",
        40,
        4.70,
        "IPS color-accurate panel with 144Hz refresh rate and USB-C.",
    ),
    (
        "ErgoCore Mechanical Keyboard",
        "CMP-KB-003",
        2,
        "129.00",
        120,
        4.90,
        "Custom tactile switches with RGB backlighting and PBT caps.",
    ),
    (
        "Titanium Smart Chef Cookware Set",
        "HM-CK-004",
        3,
        "199.95",
        60,
        4.65,
        "Non-toxic 10-piece multi-ply induction cookware set.",
    ),
    (
        "AeroStream Smart Air Purifier",
        "HM-AP-005",
        3,
        "159.00",
        75,
        4.75,
        "True HEPA filtration with real-time PM2.5 monitoring.",
    ),
    (
        "Deep Learning with PyTorch & FastAPI",
        "BK-TECH-006",
        4,
        "49.99",
        250,
        4.95,
        "Comprehensive practical manual for deploying AI microservices.",
    ),
    (
        "Designing Data-Intensive Applications",
        "BK-TECH-007",
        4,
        "54.00",
        310,
        4.98,
        "The authoritative distributed systems architecture guide.",
    ),
    (
        "All-Weather Waterproof Shell Jacket",
        "AP-JK-008",
        5,
        "189.00",
        90,
        4.60,
        "Breathable 3-layer Gore-Tex membrane with taped seams.",
    ),
    (
        "Thermal Running Tights",
        "AP-RN-009",
        5,
        "75.00",
        140,
        4.50,
        "Compression fit fabric with reflective safety strips.",
    ),
    (
        "PulseTrack GPS Multisport Smartwatch",
        "SP-SW-010",
        6,
        "349.00",
        55,
        4.80,
        "Rugged titanium bezel, dual GPS, and heart rate sensor.",
    ),
    (
        "Carbon Fiber Road Cycling Helmet",
        "SP-HL-011",
        6,
        "119.50",
        65,
        4.68,
        "Ultra-lightweight aerodynamic ventilation with MIPS.",
    ),
    (
        "Revitalizing Hyaluronic Acid Serum",
        "BT-SR-012",
        7,
        "38.00",
        220,
        4.72,
        "Triple-action hydrating peptide formula with botanicals.",
    ),
    (
        "Precision Beard & Hair Trimmer Pro",
        "BT-TR-013",
        7,
        "69.99",
        110,
        4.55,
        "Self-sharpening titanium blades with 40 length settings.",
    ),
    (
        "Robotics Exploration STEM Rover Kit",
        "TY-ST-014",
        8,
        "89.95",
        80,
        4.88,
        "Programmable Arduino-compatible obstacle-avoiding rover.",
    ),
    (
        "Terraforming Mars Strategy Board Game",
        "TY-BG-015",
        8,
        "64.99",
        95,
        4.92,
        "Award-winning resource management engine builder.",
    ),
    (
        "Bluetooth OBD2 Diagnostic Scanner",
        "AU-OB-016",
        9,
        "45.00",
        130,
        4.62,
        "Real-time engine diagnostics, code clearing, and telemetry.",
    ),
    (
        "Compact 12V Cordless Drill & Driver",
        "AU-TL-017",
        9,
        "99.00",
        70,
        4.70,
        "Brushless motor delivering 350 in-lbs torque.",
    ),
    (
        "Organic Plant Protein Powder (Vanilla)",
        "HL-PR-018",
        10,
        "39.99",
        180,
        4.67,
        "25g clean vegan protein with complete BCAA profile.",
    ),
    (
        "Ultra-Pure Omega-3 Fish Oil 1200mg",
        "HL-OM-019",
        10,
        "29.50",
        200,
        4.80,
        "Molecularly distilled wild salmon oil rich in EPA/DHA.",
    ),
    (
        "Studio Sound Condenser Microphone",
        "ELE-MC-020",
        1,
        "149.00",
        85,
        4.78,
        "Cardioid pickup capsule with zero-latency headphone jack.",
    ),
    (
        "Thunderbolt 4 Dual Display Dock",
        "CMP-DK-021",
        2,
        "229.00",
        45,
        4.65,
        "96W power delivery with 2x HDMI 2.1 and SD card reader.",
    ),
    (
        "Cold Brew Precision Coffee Maker",
        "HM-CF-022",
        3,
        "42.00",
        160,
        4.82,
        "Borosilicate glass carafe with stainless mesh filter.",
    ),
    (
        "Systems Performance: Enterprise & Cloud",
        "BK-SYS-023",
        4,
        "62.50",
        115,
        4.94,
        "Brendan Gregg's benchmark manual for Linux tuning.",
    ),
    (
        "Merino Wool Everyday Hoodie",
        "AP-HD-024",
        5,
        "135.00",
        80,
        4.74,
        "100% natural thermoregulating merino knit fleece.",
    ),
    (
        "Adjustable Cast Iron Kettlebell 10-40lb",
        "SP-KB-025",
        6,
        "149.99",
        50,
        4.86,
        "Quick-adjust selector dial with ergonomic powder coat.",
    ),
    (
        "Ultrasonic Aromatherapy Diffuser",
        "BT-DF-026",
        7,
        "34.99",
        175,
        4.58,
        "Whisper-quiet ambient light mist diffuser.",
    ),
    (
        "CyberCity 3D Wooden Puzzle Architecture",
        "TY-PZ-027",
        8,
        "49.00",
        105,
        4.76,
        "Laser-cut mechanical puzzle with solar-powered gear motion.",
    ),
    (
        "Digital Tire Inflator with LED Gauge",
        "AU-IF-028",
        9,
        "39.95",
        140,
        4.66,
        "Fast 150 PSI auto-shutoff compressor with 12V car adapter.",
    ),
    (
        "Daily Electrolyte Hydration Pack (30ct)",
        "HL-EL-029",
        10,
        "24.99",
        300,
        4.83,
        "Zero sugar electrolyte formula packed with minerals.",
    ),
    (
        "MagCharge 3-in-1 Fast Wireless Stand",
        "ELE-WC-030",
        1,
        "79.99",
        125,
        4.71,
        "Fast Qi2 magnetic charging for phone, earbuds, and watch.",
    ),
]

ORDER_STATUSES = ["completed", "shipped", "processing", "pending"]
PAYMENT_METHODS = ["credit_card", "paypal", "apple_pay", "bank_transfer"]
STREET_NAMES = ["Main", "Oak", "Pine", "Cedar", "Maple", "Elm", "Washington"]


def seed_database(reset: bool = True) -> dict[str, int]:
    """
    Seeds database with 5 relational tables:
    - 10 categories
    - 40 customers
    - 30 products
    - 60 orders
    - 200 order items (Largest table: exactly 200 records)
    """
    if reset:
        reset_schema()

    random.seed(42)  # Deterministic seed for reproducibility
    now = datetime.now(timezone.utc)

    counts = {
        "categories": 0,
        "customers": 0,
        "products": 0,
        "orders": 0,
        "order_items": 0,
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Seed Categories (10 records, 6 columns)
            logger.info("Seeding 10 categories...")
            category_ids = []
            for cat in CATEGORIES_DATA:
                created_date = now - timedelta(days=random.randint(60, 180))
                cur.execute(
                    """
                    INSERT INTO categories (
                        name, slug, description, is_active, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        cat["name"],
                        cat["slug"],
                        cat["description"],
                        cat["is_active"],
                        created_date,
                    ),
                )
                category_ids.append(cur.fetchone()[0])
            counts["categories"] = len(category_ids)

            # 2. Seed Customers (40 records, 9 columns)
            logger.info("Seeding 40 customers...")
            customer_ids = []
            for i in range(40):
                first = FIRST_NAMES[i]
                last = LAST_NAMES[i]
                email = f"{first.lower()}.{last.lower()}{i+10}@example.com"
                p1, p2 = random.randint(100, 999), random.randint(1000, 9999)
                phone = f"+1-555-{p1:03d}-{p2:04d}"
                street_num = random.randint(100, 9999)
                street = random.choice(STREET_NAMES)
                apt = random.randint(1, 80)
                address = f"{street_num} {street} St, Apt {apt}"
                city = CITIES[i % len(CITIES)]
                country = "United States"
                cust_date = now - timedelta(days=random.randint(30, 120))

                cur.execute(
                    """
                    INSERT INTO customers (
                        first_name, last_name, email, phone,
                        address, city, country, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        first,
                        last,
                        email,
                        phone,
                        address,
                        city,
                        country,
                        cust_date,
                    ),
                )
                customer_ids.append(cur.fetchone()[0])
            counts["customers"] = len(customer_ids)

            # 3. Seed Products (30 records, 10 columns)
            logger.info("Seeding 30 products...")
            product_records = []
            for prod in PRODUCTS_SEED:
                name, sku, cat_idx, price_str, stock, rating, desc = prod
                cat_id = category_ids[cat_idx - 1]
                price = Decimal(price_str)
                prod_date = now - timedelta(days=random.randint(20, 90))

                cur.execute(
                    """
                    INSERT INTO products (
                        category_id, name, sku, description, price,
                        stock_quantity, rating, is_available, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, price;
                    """,
                    (
                        cat_id,
                        name,
                        sku,
                        desc,
                        price,
                        stock,
                        rating,
                        True,
                        prod_date,
                    ),
                )
                p_id, p_price = cur.fetchone()
                product_records.append({"id": p_id, "price": Decimal(str(p_price))})
            counts["products"] = len(product_records)

            # 4. Seed Orders (60 records, 8 columns)
            logger.info("Seeding 60 orders...")
            order_ids = []
            for i in range(60):
                cust_id = random.choice(customer_ids)
                status = random.choice(ORDER_STATUSES)
                pay_method = random.choice(PAYMENT_METHODS)
                track_num = (
                    f"TRK-{random.randint(10000000, 99999999)}"
                    if status in ("shipped", "completed")
                    else None
                )
                c_way = random.randint(100, 999)
                suite = random.randint(10, 99)
                city = random.choice(CITIES)
                shipping_addr = f"{c_way} Commerce Way, Suite {suite}, {city}, US"
                order_date = now - timedelta(
                    days=random.randint(1, 60), hours=random.randint(1, 23)
                )

                cur.execute(
                    """
                    INSERT INTO orders (
                        customer_id, order_status, total_amount,
                        shipping_address, payment_method, tracking_number,
                        ordered_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        cust_id,
                        status,
                        Decimal("0.00"),
                        shipping_addr,
                        pay_method,
                        track_num,
                        order_date,
                    ),
                )
                order_ids.append(cur.fetchone()[0])
            counts["orders"] = len(order_ids)

            # 5. Seed Order Items (Exact 200 records in largest table, 8 columns)
            logger.info("Seeding exactly 200 order items into largest table...")
            total_items_target = 200
            order_totals: dict[int, Decimal] = {
                oid: Decimal("0.00") for oid in order_ids
            }

            items_seeded = 0
            # Ensure every order gets at least 2 items (60 * 2 = 120 items)
            for oid in order_ids:
                for _ in range(2):
                    prod = random.choice(product_records)
                    qty = random.randint(1, 4)
                    unit_price = prod["price"]
                    discount = Decimal("0.00")
                    if random.random() < 0.25:
                        discount = (
                            unit_price * Decimal(str(qty)) * Decimal("0.10")
                        ).quantize(Decimal("0.01"))
                    subtotal = (unit_price * Decimal(str(qty))) - discount
                    item_date = now - timedelta(days=random.randint(1, 60))

                    cur.execute(
                        """
                        INSERT INTO order_items (
                            order_id, product_id, quantity, unit_price,
                            discount_amount, subtotal, created_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """,
                        (
                            oid,
                            prod["id"],
                            qty,
                            unit_price,
                            discount,
                            subtotal,
                            item_date,
                        ),
                    )
                    order_totals[oid] += subtotal
                    items_seeded += 1

            # Seed remaining items to hit exactly 200 items (200 - 120 = 80 items)
            remaining_to_seed = total_items_target - items_seeded
            for _ in range(remaining_to_seed):
                oid = random.choice(order_ids)
                prod = random.choice(product_records)
                qty = random.randint(1, 3)
                unit_price = prod["price"]
                discount = Decimal("0.00")
                if random.random() < 0.20:
                    discount = (
                        unit_price * Decimal(str(qty)) * Decimal("0.15")
                    ).quantize(Decimal("0.01"))
                subtotal = (unit_price * Decimal(str(qty))) - discount
                item_date = now - timedelta(days=random.randint(1, 60))

                cur.execute(
                    """
                    INSERT INTO order_items (
                        order_id, product_id, quantity, unit_price,
                        discount_amount, subtotal, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        oid,
                        prod["id"],
                        qty,
                        unit_price,
                        discount,
                        subtotal,
                        item_date,
                    ),
                )
                order_totals[oid] += subtotal
                items_seeded += 1

            counts["order_items"] = items_seeded

            # Update orders with correct calculated total_amount
            for oid, total in order_totals.items():
                cur.execute(
                    "UPDATE orders SET total_amount = %s WHERE id = %s;",
                    (total, oid),
                )

        conn.commit()

    logger.info("Seeding complete: %s", counts)
    return counts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Beginning database reset and seeding...")
    result = seed_database(reset=True)
    print("Database successfully seeded:")
    for tbl, count in result.items():
        print(f"  - {tbl}: {count} records")
