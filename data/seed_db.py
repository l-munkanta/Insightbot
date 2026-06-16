import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "data/business.db"

def create_and_seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
    DROP TABLE IF EXISTS interactions;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS customers;
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        company TEXT,
        plan_tier TEXT,
        monthly_spend REAL,
        signup_date TEXT,
        country TEXT
    );
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        amount REAL,
        product TEXT,
        status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    CREATE TABLE interactions (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        type TEXT,
        interaction_date TEXT,
        sentiment_score REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    """)

    plans = ["starter", "pro", "enterprise"]
    products = ["Analytics Suite", "Data Connector", "API Access", "Dashboard Pro"]
    interaction_types = ["support_ticket", "sales_call", "email", "demo_request"]
    countries = ["DE", "US", "GB", "FR", "NL"]

    now = datetime.now()
    base_date = now - timedelta(days=540)

    for i in range(1, 201):
        signup = base_date + timedelta(days=random.randint(0, 360))
        plan = random.choice(plans)
        spend = {
            "starter": random.uniform(50, 200),
            "pro": random.uniform(200, 800),
            "enterprise": random.uniform(800, 5000)
        }[plan]

        c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", (
            i, f"Customer {i}", f"Company {i}", plan,
            round(spend, 2), signup.strftime("%Y-%m-%d"),
            random.choice(countries)
        ))

        if i <= 100:
            num_orders = random.randint(1, 8)
            max_days = (now - signup).days
            for _ in range(num_orders):
                days_ago = random.randint(0, min(60, max_days))
                order_date = now - timedelta(days=days_ago)
                c.execute("INSERT INTO orders VALUES (NULL,?,?,?,?,?)", (
                    i, order_date.strftime("%Y-%m-%d"),
                    round(random.uniform(100, 2000), 2),
                    random.choice(products),
                    random.choice(["completed", "pending", "cancelled"])
                ))
        else:
            num_orders = random.randint(0, 5)
            max_days = (now - signup).days
            for _ in range(num_orders):
                days_ago = random.randint(95, max_days) if max_days > 95 else max_days
                order_date = now - timedelta(days=days_ago)
                c.execute("INSERT INTO orders VALUES (NULL,?,?,?,?,?)", (
                    i, order_date.strftime("%Y-%m-%d"),
                    round(random.uniform(100, 2000), 2),
                    random.choice(products),
                    random.choice(["completed", "pending", "cancelled"])
                ))

        for _ in range(random.randint(0, 8)):
            max_days = (now - signup).days
            int_date = now - timedelta(days=random.randint(0, max_days))
            c.execute("INSERT INTO interactions VALUES (NULL,?,?,?,?)", (
                i, random.choice(interaction_types),
                int_date.strftime("%Y-%m-%d"),
                round(random.uniform(0.1, 1.0), 2)
            ))

    conn.commit()
    conn.close()
    print("Done! Database recreated with a balanced mix of active and churned customers.")

if __name__ == "__main__":
    create_and_seed()