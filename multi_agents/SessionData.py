import streamlit as st
import json
import os
import re
from datetime import datetime

SESSIONS_DIR = "chat_history"


class SessionData:
    def __init__(self):
        self.filename = ""
        # self.uuid = uuid.uuid4().hex
        self.title = "new chat"
        self.created_at = datetime.now().isoformat()
        self.latest = self.created_at
        self.messages = []
        self.message_count = 0
        # self.create_new_session()

    def dict_to_structure(self, data: dict):
        self.filename = data.get("filename", "")
        # self.uuid = data.get("uuid", uuid.uuid4().hex)
        self.title = data.get("title", "new_chat")
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.latest = data.get("latest", datetime.now().isoformat())
        self.message_count = data.get("message_count", 0)
        self.messages = data.get("messages", [])
        return self

    def load_from_file(self, filename):
        filepath = os.path.join(SESSIONS_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.dict_to_structure(data)
                return self
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                return None
        else:
            print(f"Error reading {filepath}")
            return None

    def structure_to_dict(self):
        return {
            "filename": self.filename,
            # "uuid": self.uuid,
            "title": self.title,
            "created_at": self.created_at,
            "latest": self.latest,
            "message_count": self.message_count,
            "messages": self.messages.copy(),  # 避免外部修改原列表
        }
        
    def exists(self, filename) -> bool:
        return (filename in os.listdir(SESSIONS_DIR))

    def sanitize_title(self):
        self.title = re.sub(r'[\\/*?:"<>|]', "", self.title).strip(". ")  # type: ignore
        if len(self.title) > 20:
            self.title = self.title[:20]

    def get_unique_filename(self):
        base_name = self.title
        filename = f"{base_name}.json"
        # exists = any(
        #     filename == session.filename for session in st.session_state.sessions
        # )
        # exists = (filename in os.listdir(SESSIONS_DIR))
        if self.exists(filename): 
            suffix = 0
            while self.exists(filename):
                suffix += 1
                filename = f"{base_name}_{suffix}.json"
        if not self.exists(filename):
            self.filename = filename

    def create_new_session(self):
        self.sanitize_title()
        self.get_unique_filename()
        self.save_session_into_file()
        # st.session_state.sessions.append(self.get_data()).sort(key=lambda x: x.created_at, reverse=True)
        # self.update_session_state()
        return self

    def save_session_into_file(self):
        filepath = os.path.join(SESSIONS_DIR, self.filename)
        data = self.structure_to_dict()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"incident happened when writing into {filepath}: {e}\n")

    def rename_file(self, old_filename):
        old_filepath = os.path.join(SESSIONS_DIR, old_filename)
        new_filepath = os.path.join(SESSIONS_DIR, self.filename)
        self.latest = datetime.now().isoformat()
        data = self.structure_to_dict()
        try:
            with open(old_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"incident happened when writing into {old_filepath}: {e}\n")
        os.rename(old_filepath, new_filepath)

    def dump_latest_messages(self):
        self.message_count += 3
        self.messages = st.session_state.messages.copy()
        self.latest = datetime.now().isoformat()
        filepath = os.path.join(SESSIONS_DIR, self.filename)
        data = self.structure_to_dict()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"incident happened when writing into {filepath}: {e}\n")

    def update_session_title(self, new_title):
        self.latest = datetime.now().isoformat()
        old_filename = self.filename
        self.title = new_title
        self.sanitize_title()
        self.get_unique_filename()
        if old_filename != self.filename:
            self.rename_file(old_filename)

    def delete_session(self):
        filepath = os.path.join(SESSIONS_DIR, self.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        # always check if list of sessions had any members after deletion

    # def get_session(self):
    #     return self


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
