import streamlit as st
import json
import os
import re
from datetime import datetime
from openai import OpenAI

import session_helpler

st.markdown(
    """
    <style>
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        margin-bottom: 1rem;
        }
    .second_header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def styled_text(class_type:str, text_content:str, help_content:str=""):
    html = f'<div class="{class_type}"> {text_content} </div>'
    st.markdown(
        html,
        help=help_content,
    )

with st.sidebar: 
    styled_text("sidebar-header", "chat history")
    col_newchat, col_refresh = st.columns([5, 1])
    with col_newchat:
        if st.button("➕ add new chat", use_container_width=True):
            new_session = session_helpler.SessionData().update_session_state()
            st.rerun()
    with col_refresh:
        if st.button("🔄", help="refresh chat history"):
            st.rerun()
    st.divider()

    if not st.session_state.sessions:
        st.info("no chat, start one by 「 add new chat 」")
    else:
        for session in st.session_state.sessions:
            session.update_session_state()
            title_display = session.title
            if len(title_display) > 20:
                title_display = title_display[:17] + "..."
            col_title, col_edit = st.columns([5, 1])
            with col_title:
                if st.session_state.editing_id == session.uuid:
                    new_title = st.text_input(
                        "chat title",
                        value=session.title,
                        key=st.session_state.new_title_buffer,
                        label_visibility="visible",
                        placeholder="editing new title..."
                    )
                else:
                    st.markdown(f"**{session.title}**")

            with col_edit:
                if st.session_state.editing_id == session.uuid:
                    if st.button("💾", help="save new title"):
                        new_title = st.session_state.get("new_title_buffer", session.title)
                        session.save_new_title(new_title)
                        st.session_state.new_title_buffer = None
                        st.session_state.editing_id = None
                        # session_helpler.update_title(session["uuid"], new_title)
                else:
                    if st.button("✍️", help="edit title"):
                        st.session_state.editing_id = session.uuid
                        st.rerun()
    st.divider()

    if len(st.session_state.sessions) > 0:
        if st.button("🗑️ delete current chat", use_container_width=True):
            st.session_state.current_title.delete_session()
            if len(st.session_state.sessions) > 0:
                current_session = st.session_state.sessions[0]
                current_session.update_session_state()
            else:
                current_session = session_helpler.SessionData()
                current_session.update_session_state()
            st.rerun()
    st.divider()

    styled_text("sidebar-header", "select models")
