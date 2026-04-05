import streamlit as st
import os
from typing import Optional
from SessionData import SessionData

SESSIONS_DIR = "chat_history"

def session_into_list(filename):
    st.session_state.sessions.insert(0, filename)

def activate_current_session(filename):
    session = SessionData().load_from_file(filename)
    if isinstance(session, SessionData):
        st.session_state.current_session = session
        st.session_state.messages = session.messages

def get_list_sessions():
    try:
        files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
    except FileNotFoundError:
        st.session_state.sessions = []
        return
    st.session_state.sessions = files


def initialize():
    if "initialized" in st.session_state:
        return

    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)

    if "sessions" not in st.session_state:
        st.session_state.sessions = []  # session.filename
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_session" not in st.session_state:
        st.session_state.current_session: Optional[SessionData] = None # type: ignore
    if "editing_file" not in st.session_state:
        st.session_state.editing_file = None
    if "new_title_buffer" not in st.session_state:
        st.session_state.new_title_buffer = None

    st.session_state.initialized = True
    get_list_sessions()
    if st.session_state.sessions:
        activate_current_session(st.session_state.sessions[0])
    st.session_state.initialized = True
