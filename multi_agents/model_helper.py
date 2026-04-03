import streamlit as st
import json
import os
import re
from datetime import datetime
from openai import OpenAI


def get_available_models():
    models_config = {}
    if "models" in st.secrets:
        for model_name in st.secrets["models"]:
            model_info = st.secrets["models"][model_name]
            models_config[model_name] = {
                "api_key": model_info.get("api_key", ""),
                "base_url": model_info.get("base_url", ""),
                "display_name": model_info.get("display_name", model_name),
            }
    else:
        models_config = {
            "deepseek-chat": {
            "api_key": st.secrets.get("DEEPSEEK_API_KEY", ""),
            "base_url": "https://api.deepseek.com",
            "display_name": "DeepSeek Chat",
            }
        }
    return models_config

def initialize():
    if "model_name" not in st.session_state:
        st.session_state.model_name = "deepseek-chat"
