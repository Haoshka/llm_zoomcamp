import streamlit as st
import requests
import os

# --- CONFIG ---
st.set_page_config(
    page_title="Freight Document Expert",
    page_icon="🚢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Main container */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .freight-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .freight-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .freight-subtitle {
        color: #e0e7ff;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Question bubble */
    .question-bubble {
        background-color: #dbeafe;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    /* Answer bubble */
    .answer-bubble {
        background-color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 4px 18px;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Icons */
    .icon-container {
        display: inline-block;
        width: 30px;
        height: 30px;
        background-color: #3b82f6;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
    }
    
    /* Feedback section */
    .feedback-section {
        background-color: #f1f5f9;
        padding: 0.5rem;
        border-radius: 8px;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND API URL ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

# --- HEADER ---
st.markdown("""
    <div class="freight-header">
        <h1 class="freight-title">🚢 Freight Document Expert</h1>
        <p class="freight-subtitle">Your AI Assistant for International Shipping Documents</p>
    </div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "last_conversation_id" not in st.session_state:
    st.session_state.last_conversation_id = None
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# --- SIDEBAR INFO ---
with st.sidebar:
    st.header("📋 About")
    st.info("""
    This AI assistant helps you understand freight forwarding documents including:
    
    - 📄 Bills of Lading
    - 📦 Commercial Invoices
    - 🛃 Customs Documents
    - 🚚 Packing Lists
    - ✈️ Air Waybills
    - 🚢 Sea Waybills
    
    Ask any question about shipping documents!
    """)
    
    st.header("💡 Example Questions")
    st.markdown("""
    - What is a Bill of Lading?
    - Who issues a commercial invoice?
    - What documents are needed for sea freight?
    - Explain the difference between air and sea waybills
    """)

# --- MAIN CHAT INTERFACE ---
st.markdown("### 💬 Ask Your Question")

# Input with dynamic key to clear after submission
question = st.text_input(
    "Type your question here...",
    key=f"question_input_{st.session_state.input_key}",
    placeholder="e.g., What is a Bill of Lading and who issues it?"
)

col1, col2 = st.columns([6, 1])
with col1:
    ask_button = st.button("🔍 Ask Question", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️", help="Clear history"):
        st.session_state.conversation_history = []
        st.rerun()

if ask_button:
    if not question.strip():
        st.warning("⚠️ Please enter a question about freight forwarding documents.")
    else:
        try:
            with st.spinner("🔄 Consulting freight document database..."):
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
                
                # Clear input by incrementing key
                st.session_state.input_key += 1
                
                st.success("✅ Answer retrieved from freight document database!")
                st.rerun()
            else:
                st.error(f"❌ Error: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Please ensure the Flask server is running.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

# --- DISPLAY CONVERSATION HISTORY ---
if st.session_state.conversation_history:
    st.markdown("---")
    st.markdown("### 📝 Conversation History")
    
    for idx, item in enumerate(reversed(st.session_state.conversation_history)):
        # Question
        st.markdown(f"""
            <div class="question-bubble">
                <strong>❓ Your Question:</strong><br>
                {item['question']}
            </div>
        """, unsafe_allow_html=True)
        
        # Answer
        st.markdown(f"""
            <div class="answer-bubble">
                <strong>🤖 Expert Answer:</strong><br>
                {item['answer']}
            </div>
        """, unsafe_allow_html=True)

        # Feedback buttons
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 4])
        
        feedback_key_base = f"{item['conversation_id']}_{idx}"
        
        with col1:
            if st.button("👍 Helpful", key=f"pos_{feedback_key_base}"):
                try:
                    requests.post(
                        f"{BACKEND_URL}/feedback",
                        json={
                            "conversation_id": item["conversation_id"],
                            "feedback": 1,
                        },
                    )
                    st.toast("✅ Thanks for your positive feedback!", icon="🙌")
                except Exception as e:
                    st.error(f"Feedback failed: {e}")

        with col2:
            if st.button("👎 Not Helpful", key=f"neg_{feedback_key_base}"):
                try:
                    requests.post(
                        f"{BACKEND_URL}/feedback",
                        json={
                            "conversation_id": item["conversation_id"],
                            "feedback": -1,
                        },
                    )
                    st.toast("📝 Feedback recorded. We'll improve!", icon="🛠️")
                except Exception as e:
                    st.error(f"Feedback failed: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()
else:
    st.info("👋 Welcome! Ask your first question about freight forwarding documents to get started.")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 1rem;'>
        <small>
        🚢 Freight Document Expert | Powered by RAG Technology<br>
        Backend: Flask | Database: PostgreSQL | Frontend: Streamlit
        </small>
    </div>
""", unsafe_allow_html=True)