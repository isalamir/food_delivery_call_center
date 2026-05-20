"""Seed the database with realistic mock data at scale."""

from datetime import datetime, timedelta, timezone
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.driver import Driver
from app.models.identity import IdentityLookup
from app.models.order import Order
from app.models.restaurant import Restaurant


async def seed_database(db: AsyncSession) -> None:
    """Populate DB with scale mock data: 20 customers, 15 drivers, 7 restaurants, 50 orders."""
    result = await db.execute(select(Customer))
    if result.scalars().first() is not None:
        return  # Already seeded

    now = datetime.now(timezone.utc)

    # ── 1. Generate 7 Restaurants ──────────────────────────────────────
    restaurants_data = [
        ("Burger Palace", "+962791234561", "Enter through side door. Shelf on left.", {"classic_burger": True, "fries": False, "cola": True}),
        ("Sushi Express", "+962791234562", "Ring back bell. Counter on right.", {"salmon_roll": True, "miso_soup": True, "edamame": False}),
        ("Pizza Zone", "+962791234563", "Front counter pickup.", {"margherita": True, "pepperoni": True, "garlic_bread": True}),
        ("Taco Corner", "+962791234564", "Drive-thru window 2.", {"beef_taco": True, "nachos": True, "churros": False}),
        ("Green & Lean", "+962791234565", "Main pickup shelf near entrance.", {"caesar_salad": True, "green_smoothie": True}),
        ("Pasta Bella", "+962791234566", "Ask at the bar.", {"lasagna": True, "spaghetti": True, "tiramisu": True}),
        ("Sweet Treats", "+962791234567", "Bakery counter pickup.", {"cupcake": True, "donut": True, "waffle": False}),
    ]

    restaurants = []
    for i, (name, phone, instructions, inventory) in enumerate(restaurants_data):
        partner_id = str(5001 + i)  # 5001 to 5007
        restaurants.append(
            Restaurant(
                partner_id=partner_id,
                name=name,
                menu_status="open" if i < 6 else "paused",  # Last one is paused
                contact_phone=phone,
                pickup_instructions=instructions,
                payout_balance=round(random.uniform(200.0, 1500.0), 2),
                menu_inventory=inventory,
            )
        )

    # ── 2. Generate 20 Customers ──────────────────────────────────────
    customer_names = [
        "Sarah Ahmed", "Omar Khalil", "Lina Mansour", "Faisal Tariq",
        "Yasmine Rami", "Hamza Nour", "Mona Majed", "Zaid Faris",
        "Rania Samer", "Kareem Jad", "Leila Hani", "Tareq Basil",
        "Dina Wael", "Adam Shaker", "Nour Salim", "Maya Fuad",
        "Hasan Adel", "Judy Ghassan", "Khalid Nader", "Reem Maher"
    ]

    customers = []
    for i, name in enumerate(customer_names):
        customer_id = str(1001 + i)  # 1001 to 1020
        # Create varying strike counts (e.g. Lina Mansour (1003) has 3 strikes to trigger escalation)
        strike_count = 3 if i == 2 else random.choices([0, 1, 2], weights=[0.7, 0.2, 0.1])[0]
        customers.append(
            Customer(
                customer_id=customer_id,
                name=name,
                active_order_id=None,  # Linked later
                refund_strike_count=strike_count,
            )
        )

    # ── 3. Generate 15 Drivers ────────────────────────────────────────
    driver_names = [
        "Tariq Hasan", "Nadia Farouk", "Samer Judeh", "Rayan Odeh",
        "Dana Saleh", "Murad Qasem", "Aya Jabr", "Fadi Haddad",
        "Luma Halabi", "Rami Khoury", "Salma Kanaan", "Waseem Masri",
        "Hana Bitar", "Majd Naser", "Omar Said"
    ]

    drivers = []
    for i, name in enumerate(driver_names):
        driver_id = str(2001 + i)  # 2001 to 2015
        # Variations in status and incident counts
        account_status = "under_review" if i == 14 else "active"
        incident_count = random.choices([0, 1, 2, 3], weights=[0.8, 0.13, 0.05, 0.02])[0]
        drivers.append(
            Driver(
                driver_id=driver_id,
                name=name,
                current_assignment_id=None,  # Linked later
                account_status=account_status,
                pending_earnings=round(random.uniform(50.0, 300.0), 2),
                incident_count=incident_count,
            )
        )

    # ── 4. Generate 50 Orders ─────────────────────────────────────────
    # Link them in a distributed, logical way
    statuses = ["delivered", "preparing", "picked_up", "cancelled", "refunded"]
    stages = ["pre-prep", "in-prep", "ready", "dispatched"]
    payment_methods = ["cash", "visa", "apple_pay"]

    orders = []
    for i in range(50):
        order_id = str(3001 + i)  # 3001 to 3050

        # Cycle/randomize links
        cust = customers[i % 20]
        rest = restaurants[i % 7]
        driver = drivers[i % 15] if i % 4 != 0 else None  # 25% of orders don't have a driver assigned

        # Create realistic combinations of status and stage
        if i < 30:
            status = "delivered"
            stage = "dispatched"
            eta = None
        elif i < 40:
            status = "preparing"
            stage = "pre-prep" if i % 2 == 0 else "in-prep"
            # Setting some ETAs to tomorrow (May 21, 2026)
            if i % 2 == 0:
                eta = now + timedelta(days=1) + timedelta(minutes=random.randint(15, 45))
            else:
                eta = now + timedelta(minutes=random.randint(15, 45))
        elif i < 46:
            status = "picked_up"
            stage = "dispatched"
            # Setting some ETAs to tomorrow (May 21, 2026)
            if i % 2 == 0:
                eta = now + timedelta(days=1) + timedelta(minutes=random.randint(5, 20))
            else:
                eta = now + timedelta(minutes=random.randint(5, 20))
        elif i < 48:
            status = "cancelled"
            stage = "pre-prep"
            eta = None
        else:
            status = "refunded"
            stage = "ready"
            eta = None

        total_price = round(random.uniform(12.50, 85.00), 2)
        driver_payout = round(total_price * 0.15 + 2.50, 2) if driver else 0.0
        pay_method = payment_methods[i % 3]

        orders.append(
            Order(
                order_id=order_id,
                customer_id=cust.customer_id,
                restaurant_id=rest.partner_id,
                driver_id=driver.driver_id if driver else None,
                status=status,
                stage=stage,
                eta=eta,
                total_price=total_price,
                driver_payout=driver_payout,
                payment_method=pay_method,
            )
        )

        # Set active references for the latest orders
        if status in ["preparing", "picked_up"]:
            cust.active_order_id = order_id
            if driver:
                driver.current_assignment_id = order_id

    # ── 5. Generate Identity Lookups ─────────────────────────────────
    identities = []
    lookup_id_counter = 4001

    # Add Customers (Phone range: +962791000001 to +962791000020)
    for i, cust in enumerate(customers):
        identities.append(
            IdentityLookup(
                identity_id=str(lookup_id_counter),
                phone_number=f"+9627910000{i+1:02d}",
                actor_type="customer",
                linked_id=cust.customer_id,
            )
        )
        lookup_id_counter += 1

    # Add Restaurants (Phone range: +962792000001 to +962792000007)
    for i, rest in enumerate(restaurants):
        identities.append(
            IdentityLookup(
                identity_id=str(lookup_id_counter),
                phone_number=f"+9627920000{i+1:02d}",
                actor_type="restaurant",
                linked_id=rest.partner_id,
            )
        )
        lookup_id_counter += 1

    # Add Drivers (Phone range: +962793000001 to +962793000015)
    for i, drv in enumerate(drivers):
        identities.append(
            IdentityLookup(
                identity_id=str(lookup_id_counter),
                phone_number=f"+9627930000{i+1:02d}",
                actor_type="driver",
                linked_id=drv.driver_id,
            )
        )
        lookup_id_counter += 1

    # ── Commit all ───────────────────────────────────────────────────
    db.add_all(restaurants + customers + drivers + orders + identities)
    await db.commit()
    print(f"✅ Seeding complete: {len(customers)} customers, {len(drivers)} drivers, {len(restaurants)} restaurants, {len(orders)} orders.")
