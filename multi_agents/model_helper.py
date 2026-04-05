import streamlit as st
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


def convert_history_for_api(history, system_prompt, agent_name):
    messages = [{"role": "system", "content": system_prompt}]
    for message in history:
        if message["role"] == agent_name:
            messages.append({"role": "assistant", "content": message["content"]})
        else:
            content = f"{message['role']}: {message['content']}"
            messages.append({"role": "user", "content": content})
    return messages



def stream_agent_response(history, system_prompt, agent_name, temperature=0.7):
    model_name = st.session_state.get("model_name", "deepseek-chat")
    api_key = st.session_state.get("api_key", "")
    api_base = st.session_state.get("api_base", "")

    if not api_key:
        yield "⚠️ model configs lack **API Key**"
        return

    if not api_base:
        yield "⚠️ model configs lack **Base URL**"
        return

    try:
        client = OpenAI(api_key=api_key, base_url=api_base)
    except Exception as e:
        yield f"⚠️ failed to create connection: {e}"
        return

    messages = convert_history_for_api(history, system_prompt, agent_name)

    try:
        stream = client.chat.completions.create(    # type: ignore
            model=model_name, 
            messages=messages,  # type: ignore
            stream=True, 
            temperature=temperature
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                # incase markdown dont acknowledge ~~
                yield chunk.choices[0].delta.content.replace("~~", "\\~\\~")
    except Exception as e:
        yield f"⚠️ permission denied: {e}"


def initialize():
    if "model_name" not in st.session_state:
        st.session_state.model_name = "deepseek-chat"
