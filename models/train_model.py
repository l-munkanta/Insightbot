import sqlite3
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

DB_PATH = "data/business.db"
MODEL_PATH = "models/churn_model.pkl"
CUTOFF = datetime.now() - timedelta(days=90)

def load_features():
    conn = sqlite3.connect(DB_PATH)
    customers = pd.read_sql("SELECT * FROM customers", conn)
    orders = pd.read_sql("SELECT * FROM orders", conn)
    interactions = pd.read_sql("SELECT * FROM interactions", conn)
    conn.close()

    orders["order_date"] = pd.to_datetime(orders["order_date"])
    interactions["interaction_date"] = pd.to_datetime(interactions["interaction_date"])

    order_agg = orders.groupby("customer_id").agg(
        total_orders=("id", "count"),
        avg_order_value=("amount", "mean"),
        last_order_date=("order_date", "max")
    ).reset_index()

    int_agg = interactions.groupby("customer_id").agg(
        interaction_count=("id", "count"),
        avg_sentiment=("sentiment_score", "mean")
    ).reset_index()

    df = customers.merge(order_agg, left_on="id", right_on="customer_id", how="left")
    df = df.merge(int_agg, left_on="id", right_on="customer_id", how="left")

    df["signup_date"] = pd.to_datetime(df["signup_date"])
    df["days_since_signup"] = (datetime.now() - df["signup_date"]).dt.days
    df["is_churned"] = (df["last_order_date"] < CUTOFF) | df["last_order_date"].isna()
    df["is_churned"] = df["is_churned"].astype(int)

    df.fillna({
        "total_orders": 0,
        "avg_order_value": 0,
        "interaction_count": 0,
        "avg_sentiment": 0.5
    }, inplace=True)

    plan_map = {"starter": 0, "pro": 1, "enterprise": 2}
    df["plan_encoded"] = df["plan_tier"].map(plan_map)

    features = [
        "days_since_signup", "total_orders", "avg_order_value",
        "interaction_count", "avg_sentiment", "monthly_spend", "plan_encoded"
    ]
    return df, features

def train():
    df, features = load_features()
    X = df[features]
    y = df["is_churned"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    print(classification_report(y_test, model.predict(X_test)))

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "features": features}, f)

    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()