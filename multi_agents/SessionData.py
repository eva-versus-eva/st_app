import streamlit as st
import json
import os
import re
from datetime import datetime

SESSIONS_DIR = "chat_history"


class SessionData:
    def __init__(self):
        self.filename = ""
        self.title = "new chat"
        self.created_at = datetime.now().isoformat()
        self.latest = self.created_at
        self.messages = []
        self.message_count = 0

    def dict_to_structure(self, data: dict):
        self.filename = data.get("filename", "")
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
