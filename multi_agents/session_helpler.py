import streamlit as st
import json
import os
import re
import uuid
from datetime import datetime
from openai import OpenAI
from typing import Optional

SESSIONS_DIR = "chat_history"

class SessionData:
    def __init__(self):
        self.filename = ""
        self.uuid = uuid.uuid4().hex
        self.title = "new_chat"
        self.created_at = datetime.now().isoformat()
        self.messages = []
        self.message_count = 0

        self.create_new_session()

    def get_data(self):
        return {
            "filename": self.filename,
            "uuid": self.uuid,
            "title": self.title,
            "created_at": self.created_at,
            "messages": self.messages.copy(),   # 避免外部修改原列表
            "message_count": self.message_count,
        }

    def update_from_dict(self, data: dict):
        self.filename = data.get("filename", "")
        self.uuid = data.get("uuid", uuid.uuid4().hex)
        self.title = data.get("title", "new_chat")
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.messages = data.get("messages", [])
        self.message_count = data.get("message_count", 0)
        return self

    def sanitize_title(self, title):
        title = re.sub(r'[\\/*?:"<>|]', "", title).strip(". ")
        if len(title) > 20:
            title = title[:20]
            return title

    def get_unique_filename(self, base_name):
        filename = f"{base_name}.json"
        exists = any(filename == session["filename"] for session in st.session_state.sessions)
        if not exists:
            # if not os.path.exists(os.path.join(SESSIONS_DIR, filename)):
            return filename
        else:
            return f"{base_name}_{self.uuid}.json"

    def create_new_session(self):
        self.title = self.sanitize_title(self.title)
        self.filename = self.get_unique_filename(self.title)
        self.save_session_into_file()
        st.session_state.sessions.append(self.get_data()).sort(key=lambda x: x.created_at, reverse=True)
        self.update_session_state()

    def save_session_into_file(self):
        filepath = os.path.join(SESSIONS_DIR, self.filename)
        data = self.get_data()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"incident happened when writing into {filepath}: {e}\n")

    def load_from_file(self, filename):
        filepath = os.path.join(SESSIONS_DIR, f"{filename}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.update_from_dict(data)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    def save_file(self, new_title, new_filename):
        old_filepath = os.path.join(SESSIONS_DIR, self.filename)
        new_filepath = os.path.join(SESSIONS_DIR, new_filename)
        if old_filepath != new_filepath:
            with open(old_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["title"] = new_title
            data["filename"] = new_filename
            m_length = len(st.session_state.messages)
            if data["message_count"] != m_length:
                data["messages"] += st.session_state.messages
                data["message_count"] = m_length
            with open(old_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.rename(old_filepath, new_filepath)
            
    def update_session_file(self, new_title):
        new_title = self.sanitize_title(new_title)
        new_filename = self.get_unique_filename(new_title)
        self.save_file(new_title, new_filename)
        self.title = new_title
        self.filename = new_filename
        self.update_session_state()


    def delete_session(self):
        filepath = os.path.join(SESSIONS_DIR, self.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        new_list = [s for s in st.session_state.sessions if s["uuid"]==self.uuid]
        st.session_state.sessions = new_list
        # always check if list of sessions had any members after deletion

    def update_session_state(self):
        st.session_state.current_title = self.title
        st.session_state.messages = self.messages
        st.session_state.current_file = self.filename


# def sanitize_filename(title: str):
#     title = re.sub(r'[\\/*?:"<>|]', "", title)
#     title = title.strip(". ")
#     if len(title) > 20:
#         title = title[:20]
#     if not title:
#         title = "new chat"
#     return title


# def get_unique_filename(title: str):
#     base_name = sanitize_filename(title)
#     filename = f"{base_name}.json"
#     if not os.path.exists(os.path.join(SESSIONS_DIR, filename)):
#         return base_name
#     counter = 1
#     filename = f"{base_name}_{counter}.json"
#     while os.path.exists(os.path.join(SESSIONS_DIR, filename)):
#         counter += 1
#         filename = f"{base_name}_{counter}.json"
#     return filename


# def save_session_into_file(data: dict):
#     filepath = os.path.join(SESSIONS_DIR, data["filename"])
#     try:
#         with open(filepath, "w", encoding="utf-8") as f:
#             json.dump(data, f, ensure_ascii=False, indent=2)
#     except Exception as e:
#         print(f"incident happened when writing into {filepath}: {e}\n")

# def create_new_session():
#     data = {
#         "uuid": uuid.uuid4().hex,
#         "title": "new chat",
#         "created_at": datetime.now().isoformat(),
#         "messages": [],
#         "message_count": 0,
#     }
#     data["filename"] = get_unique_filename(data["title"])
#     save_session_into_file(data)
#     st.session_state.list_sessions.append(data)
#     return data


# def load_file(filename: str):
#     filepath = os.path.join(SESSIONS_DIR, f"{filename}.json")
#     if os.path.exists(filepath):
#         try:
#             with open(filepath, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except Exception as e:
#             print(f"Error reading {filepath}: {e}")


# def get_list_sessions():
#     if "sessions" not in st.session_state:
#         st.session_state.sessions = []
#     for filename in os.listdir(SESSIONS_DIR):
#         if filename.endswith(".json"):
#             filepath = os.path.join(SESSIONS_DIR, filename)
#             try:
#                 with open(filepath, "r", encoding="utf-8") as f:
#                     data = json.load(f)
#                     st.session_state.list_sessions.append(
#                         {
#                             "filename": filename[:-5],
#                             "uuid": data["uuid"],
#                             "title": data["title"],
#                             "created_at": data.get("created_at", None),
#                             "messages": data.get("messages", []),
#                             "message_count": len(data.get("messages", [])),
#                         }
#                     )
#             except Exception as e:
#                 print(f"Error reading {filepath}: {e}")
#                 continue
#     st.session_state.list_sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)


# def load_session_into_state(filename: Optional[str] = None, data: Optional[dict] = None):
#     if filename:
#         file_data = load_file(filename)
#         if file_data:
#             st.session_state.current_session_title = file_data.get("title", "new chat")
#             st.session_state.messages = file_data.get("messages", [])
#     elif data:
#         st.session_state.current_title = data.get("title", "new chat")
#         st.session_state.messages = data.get("messages", [])
#         st.session_state.current_filename = data.get("filename")


def get_list_sessions():
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            session = SessionData()
            session.load_from_file(filename)
            st.session_state.sessions.append(session)
    st.session_state.sessions.sort(key=lambda x: x.created_at, reverse=True)

def initialize():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
    
    if "sessions" not in st.session_state:
        st.session_state.sessions = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_title" not in st.session_state:
        st.session_state.current_title = ""
    if "current_file" not in st.session_state:
        st.session_state.current_file = ""
        
    get_list_sessions()
    if len(st.session_state.sessions) > 0:
        st.session_state.sessions[0].update_session_state()
    else:
        first_session = SessionData()
        # first_session.update_session_state()

    if "editing_id" not in st.session_state:
        st.session_state.editing_id = None
    if "new_title_buffer" not in st.session_state:
        st.session_state.new_title_buffer = None

        
    # if "current_filename" not in st.session_state:
    #     if st.session_state.list_sessions:
    #         # load local json files
    #         first_session = st.session_state.list_sessions[0]
    #         st.session_state.current_filename = first_session["filename"]
    #         load_session_into_state(filename=first_session["filename"])
    #     else:
    #         first_session = create_new_session()
    #         load_session_into_state(data=first_session)
