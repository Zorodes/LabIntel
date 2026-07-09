import streamlit as st
import asyncio
from pathlib import Path
from agent import ChemAgent
from auth import signup, login
from db import save_chat, get_chat_history
from tools.rag_service import DOCUMENTS_DIR, SUPPORTED_EXTENSIONS, build_index, list_document_files

# Page config
st.set_page_config(page_title="LabIntel", layout="wide")

# Check if user is logged in
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "chem_agent" not in st.session_state:
    st.session_state.chem_agent = None

# ============ LOGIN / SIGNUP PAGE ============
if st.session_state.user_id is None:
    st.title("LabIntel — Chemical Engineering AI")
    
    tab1, tab2 = st.tabs(["Login", "Signup"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            user_id, msg = login(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    with tab2:
        st.subheader("Signup")
        new_username = st.text_input("Username", key="signup_user")
        new_password = st.text_input("Password", type="password", key="signup_pass")
        
        if st.button("Signup"):
            user_id, msg = signup(new_username, new_password)
            if user_id:
                st.success(msg)
                st.info("Now log in with your credentials")
            else:
                st.error(msg)

# ============ MAIN APP (logged in) ============
else:
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("LabIntel — Chemical Engineering AI")
    with col2:
        if st.button("Logout"):
            st.session_state.user_id = None
            st.rerun()
    
    st.write(f"Logged in as: **{st.session_state.user_id}**")

    # Document upload and indexing
    st.sidebar.subheader("Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload reference documents",
        type=[ext.lstrip(".") for ext in sorted(SUPPORTED_EXTENSIONS)],
        accept_multiple_files=True,
    )

    if uploaded_files and st.sidebar.button("Save and index documents"):
        DOCUMENTS_DIR.mkdir(exist_ok=True)
        saved_files = []

        for uploaded_file in uploaded_files:
            safe_name = Path(uploaded_file.name).name
            destination = DOCUMENTS_DIR / safe_name
            destination.write_bytes(uploaded_file.getbuffer())
            saved_files.append(safe_name)

        with st.spinner("Building document index..."):
            try:
                _, chunk_count, indexed_files = build_index()
                st.sidebar.success(
                    f"Indexed {chunk_count} chunks from {len(indexed_files)} file(s)."
                )
                st.sidebar.caption("Saved: " + ", ".join(saved_files))
            except Exception as exc:
                st.sidebar.error(f"Indexing failed: {exc}")

    indexed_files = list_document_files()
    if indexed_files:
        st.sidebar.caption("Current files: " + ", ".join(path.name for path in indexed_files))
    else:
        st.sidebar.info("Upload documents before asking document-specific questions.")
    
    # Chat interface
    st.subheader("Ask a Question")
    query = st.text_input("Your question:")
    
    if query:
        if st.session_state.chem_agent is None:
            st.session_state.chem_agent = ChemAgent()
            asyncio.run(st.session_state.chem_agent.initialize())

        with st.spinner("Agent thinking..."):
            response = asyncio.run(st.session_state.chem_agent.ask(query))
        
        st.write("**Response:**")
        st.write(response)
        
        # Save to MongoDB
        save_chat(st.session_state.user_id, query, str(response))
        st.success("Saved to chat history")
    
    # Chat history sidebar
    st.sidebar.subheader("Chat History")
    history = get_chat_history(st.session_state.user_id, limit=10)
    
    if history:
        for entry in history:
            with st.sidebar.expander(f"Q: {entry['query'][:50]}..."):
                st.write(f"**Query:** {entry['query']}")
                st.write(f"**Response:** {entry['response']}")
                st.write(f"**Time:** {entry['timestamp']}")
    else:
        st.sidebar.info("No chat history yet")
