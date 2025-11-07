import streamlit as st
import requests
import os

# --- CONFIG ---
st.set_page_config(page_title="RAG Q&A Demo", page_icon="💬", layout="centered")

# --- BACKEND API URL ---
# Example: if Flask is running on localhost:5000 or exposed through Codespaces
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

st.title("💬 RAG Q&A Demo App")
st.caption("Powered by your containerized Flask + Postgres backend")

# --- SESSION STATE ---
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "last_conversation_id" not in st.session_state:
    st.session_state.last_conversation_id = None

# --- INPUT ---
question = st.text_input("Ask your question:")

if st.button("Ask"):
    if not question.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        try:
            with st.spinner("Fetching answer from backend..."):
                response = requests.post(
                    f"{BACKEND_URL}/question", json={"question": question}
                )

            if response.status_code == 200:
                data = response.json()
                conversation_id = data["conversation_id"]
                answer = data["answer"]

                st.session_state.last_conversation_id = conversation_id
                st.session_state.conversation_history.append(
                    {
                        "conversation_id": conversation_id,
                        "question": question,
                        "answer": answer,
                    }
                )
                st.success("✅ Answer received!")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

# --- DISPLAY HISTORY ---
st.subheader("Conversation History")
for item in reversed(st.session_state.conversation_history):
    st.markdown(f"**🧠 Question:** {item['question']}")
    st.markdown(f"**💬 Answer:** {item['answer']}")

    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Helpful", key=f"pos_{item['conversation_id']}"):
            try:
                requests.post(
                    f"{BACKEND_URL}/feedback",
                    json={
                        "conversation_id": item["conversation_id"],
                        "feedback": 1,
                    },
                )
                st.toast("Thanks for your feedback! 🙌")
            except Exception as e:
                st.error(f"Feedback failed: {e}")

    with col2:
        if st.button("👎 Not Helpful", key=f"neg_{item['conversation_id']}"):
            try:
                requests.post(
                    f"{BACKEND_URL}/feedback",
                    json={
                        "conversation_id": item["conversation_id"],
                        "feedback": -1,
                    },
                )
                st.toast("Feedback recorded 🛠️")
            except Exception as e:
                st.error(f"Feedback failed: {e}")

    st.divider()

st.markdown("---")
st.caption("Frontend: Streamlit | Backend: Flask | Database: Postgres | Monitoring: Grafana")
