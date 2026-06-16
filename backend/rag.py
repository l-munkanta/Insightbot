import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

DOCS = [
    {
        "id": "refund_policy",
        "text": "Customers on the Pro or Enterprise plan may request a full refund within 30 days of purchase. Starter plan refunds are not available after 7 days. Submit refund requests to billing@company.com."
    },
    {
        "id": "plan_features",
        "text": "Starter plan: up to 5 users, basic analytics, email support. Pro plan: unlimited users, advanced dashboards, priority support, API access. Enterprise plan: custom SLAs, dedicated account manager, SSO, and custom integrations."
    },
    {
        "id": "churn_policy",
        "text": "Customers flagged as high churn risk with a probability above 0.7 should be escalated to the Customer Success team within 48 hours. Offer a 20 percent discount or a free plan upgrade trial to retain them."
    },
    {
        "id": "data_retention",
        "text": "Customer data is retained for 7 years per EU compliance requirements. Data deletion requests are processed within 30 days under GDPR Article 17."
    },
]

_client = chromadb.EphemeralClient()
_ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
_collection = _client.get_or_create_collection(
    "business_docs",
    embedding_function=_ef
)

_collection.upsert(
    documents=[d["text"] for d in DOCS],
    ids=[d["id"] for d in DOCS]
)

def search_docs(query: str, n_results: int = 2) -> dict:
    try:
        results = _collection.query(query_texts=[query], n_results=n_results)
        return {
            "documents": results["documents"][0],
            "ids": results["ids"][0]
        }
    except Exception as e:
        return {"error": str(e)}