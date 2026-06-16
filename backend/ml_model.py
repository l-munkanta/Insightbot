import pickle
import pandas as pd
import sqlite3
from datetime import datetime

MODEL_PATH = "models/churn_model.pkl"
DB_PATH = "data/business.db"


def predict_churn(customer_id=None, top_n=10):
    try:
        with open(MODEL_PATH, "rb") as f:
            bundle = pickle.load(f)
        model = bundle["model"]

        conn = sqlite3.connect(DB_PATH)
        customers = pd.read_sql("SELECT * FROM customers", conn)
        orders = pd.read_sql("SELECT * FROM orders", conn)
        interactions = pd.read_sql("SELECT * FROM interactions", conn)
        conn.close()

        orders["order_date"] = pd.to_datetime(orders["order_date"])

        order_agg = orders.groupby("customer_id").agg(
            total_orders=("id", "count"),
            avg_order_value=("amount", "mean"),
        ).reset_index()

        int_agg = interactions.groupby("customer_id").agg(
            interaction_count=("id", "count"),
            avg_sentiment=("sentiment_score", "mean")
        ).reset_index()

        df = customers.merge(order_agg, left_on="id", right_on="customer_id", how="left")
        df = df.merge(int_agg, left_on="id", right_on="customer_id", how="left")

        df["signup_date"] = pd.to_datetime(df["signup_date"])
        df["days_since_signup"] = (datetime.now() - df["signup_date"]).dt.days

        df.fillna({
            "total_orders": 0,
            "avg_order_value": 0,
            "interaction_count": 0,
            "avg_sentiment": 0.5
        }, inplace=True)

        plan_map = {"starter": 0, "pro": 1, "enterprise": 2}
        df["plan_encoded"] = df["plan_tier"].map(plan_map).fillna(0)

        features = [
            "days_since_signup", "total_orders", "avg_order_value",
            "interaction_count", "avg_sentiment", "monthly_spend", "plan_encoded"
        ]

        X = df[features]
        probs_raw = model.predict_proba(X)

        if probs_raw.shape[1] == 1:
            only_class = model.classes_[0]
            probs = probs_raw[:, 0] if only_class == 1 else 1 - probs_raw[:, 0]
        else:
            probs = probs_raw[:, 1]

        df["churn_probability"] = probs.round(3)

        if customer_id is not None:
            row = df[df["id"] == customer_id]
            if row.empty:
                return {"predictions": [], "message": f"Customer {customer_id} not found"}
            result = row[["id", "churn_probability"]].rename(columns={"id": "customer_id"})
            return {"predictions": result.to_dict(orient="records")}

        top = df.nlargest(top_n, "churn_probability")[["id", "churn_probability"]]
        top = top.rename(columns={"id": "customer_id"})
        return {"predictions": top.to_dict(orient="records")}

    except Exception as e:
        return {"error": str(e), "predictions": []}