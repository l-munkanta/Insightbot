import streamlit as st
import httpx

API_URL = "http://localhost:8000/chat"

st.set_page_config(
    page_title="InsightBot",
    page_icon="🤖",
    layout="centered"
)

st.title("InsightBot — Enterprise Data Intelligence")
st.caption("Ask about customers, revenue, churn risk, or company policy.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the conversation history
for msg in st.session_state.messages:
    if isinstance(msg["content"], str):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Show clickable starter questions when the chat is empty
if not st.session_state.messages:
    st.markdown("**Try asking one of these:**")
    col1, col2 = st.columns(2)
    starters = [
        "Which customers have the highest monthly spend?",
        "Who are the top 10 customers at risk of churning?",
        "How many completed orders were placed this year?",
        "What is our refund policy for Pro customers?"
    ]
    for i, s in enumerate(starters):
        if [col1, col2][i % 2].button(s, key=s):
            st.session_state.pending = s
            st.rerun()

# Handle typed or clicked input
prompt = st.chat_input("Ask a business question...")
if hasattr(st.session_state, "pending"):
    prompt = st.session_state.pending
    del st.session_state.pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = httpx.post(
                    API_URL,
                    json={"messages": st.session_state.messages},
                    timeout=60.0
                )
                reply = resp.json()["reply"]
            except Exception as e:
                reply = f"Error connecting to backend: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})