import streamlit as st
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

from phase_3.pipeline import MutualFundRAG

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Mutual Fund AI Support",
    page_icon="💬",
    layout="centered",
)

# --- CACHE RAG PIPELINE ---
@st.cache_resource
def get_rag_pipeline():
    return MutualFundRAG()

rag = get_rag_pipeline()

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CUSTOM CSS FOR PAYPAL-STYLE UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #FFFFFF;
    }

    /* Hide default Streamlit elements */
    header, footer, #MainMenu {
        visibility: hidden;
        height: 0;
    }

    .stApp {
        background-color: #FFFFFF;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 800px !important;
    }

    /* Chat Container */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        margin-bottom: 100px;
    }

    /* Message Bubbles */
    .msg-row {
        display: flex;
        flex-direction: column;
        width: 100%;
    }

    .msg-row.user {
        align-items: flex-end;
    }

    .msg-row.assistant {
        align-items: flex-start;
    }

    .msg-bubble {
        max-width: 85%;
        padding: 16px 24px;
        font-size: 16px;
        line-height: 1.5;
        border-radius: 24px;
        margin-bottom: 4px;
    }

    .user .msg-bubble {
        background-color: #0070BA;
        color: white;
        border-bottom-right-radius: 4px;
    }

    .assistant .msg-bubble {
        background-color: #F5F7FA;
        color: #2C2E2F;
        border-bottom-left-radius: 4px;
        border: 1px solid #E5E7EB;
    }

    /* Assistant Card Style */
    .assistant-card {
        background-color: #FDFBFA;
        border: 1px solid #F3F1F0;
        border-radius: 16px;
        padding: 24px;
        max-width: 90%;
        margin-top: 8px;
    }

    .assistant-card p {
        margin-bottom: 16px;
        color: #2C2E2F;
    }

    .assistant-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .assistant-card li {
        margin-bottom: 12px;
        color: #0070BA;
        font-weight: 600;
        cursor: pointer;
    }

    .assistant-card li::before {
        content: "• ";
        color: #2C2E2F;
    }

    /* Input Area Fixed Bottom */
    .input-wrapper {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 800px;
        background: white;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        border-top: 1px solid #F5F7FA;
    }

    .input-row {
        display: flex;
        align-items: center;
        width: 100%;
        gap: 12px;
    }

    .hamburger-icon {
        font-size: 24px;
        color: #2C2E2F;
        cursor: pointer;
    }

    /* Style the native Streamlit chat input or custom one */
    .stChatInputContainer {
        border-radius: 30px !important;
        border: 2px solid #0070BA !important;
        padding: 4px !important;
    }

    .beta-tag {
        font-size: 12px;
        color: #6C7378;
        margin-top: 8px;
    }

    /* Links */
    a {
        color: #0070BA !important;
        text-decoration: none !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- CHAT INTERFACE ---

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Render messages from history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    
    if role == "user":
        st.markdown(f"""
        <div class="msg-row user">
            <div class="msg-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Check if it's a "card" style response (like the PayPal referral)
        is_card = "sources" in msg and msg["sources"]
        
        if is_card:
            sources_html = "".join([f"<li><a href='{s}' target='_blank'>{s.split('/')[-1].replace('-', ' ').title()}</a></li>" for s in msg["sources"]])
            st.markdown(f"""
            <div class="msg-row assistant">
                <div class="assistant-card">
                    <p>{content}</p>
                    <ul>
                        {sources_html}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row assistant">
                <div class="msg-bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER INPUT ---

# Create a placeholder for the input to keep it at the bottom
query = st.chat_input("Ask a question...")

if query:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Process with RAG
    try:
        result = rag.ask(query)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": result.get("answer", "No response."),
            "sources": result.get("sources", [])
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Error Processing Request: {str(e)}"
        })
    st.rerun()

st.markdown('<div style="text-align: center; color: #6C7378; font-size: 12px; margin-top: 10px;">Beta</div>', unsafe_allow_html=True)
