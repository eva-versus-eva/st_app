import streamlit as st
import json
import os
import re
from datetime import datetime
from openai import OpenAI

import session_helpler
import model_helper
import sidebar_helper


SESSIONS_DIR = "chat_history"
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

RESEARCHER_SYSTEM = """你是研究助手，性格严谨、逻辑清晰，善于查找和整合信息。
你的任务是为用户提供准确、结构化的答案，必要时引用来源或说明依据。
回答时使用专业但易懂的语言，避免主观臆断。"""

PM_SYSTEM = """你是产品经理助手，性格务实、善于沟通，关注用户需求和落地执行。
你的任务是从用户问题中提炼关键点，给出可操作的建议，并协调不同观点。
回答时语言简洁、重点突出，必要时可以补充实现思路或风险提示。"""

session_helpler.initialize()
model_helper.initialize()


st.set_page_config(page_title="双 Agent 智能助手", page_icon="💬", layout="wide")
st.title("🤖 双 Agent 智能助手")
st.caption("研究员 📚 + 产品经理 💼 为你提供双重视角")



# todo
def convert_history_for_api(history, system_prompt, agent_name):
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        if msg["role"] == agent_name:
            messages.append({"role": "assistant", "content": msg["content"]})
        else:
            content = f"{msg['role']}: {msg['content']}"
            messages.append({"role": "user", "content": content})
    return messages

def stream_agent_response(history, system_prompt, agent_name, temperature=0.7):
    """
    根据 st.session_state 中保存的模型配置动态创建客户端并流式生成回复
    """
    # 从 session_state 获取配置
    model_name = st.session_state.get("model_name", "deepseek-chat")
    api_key = st.session_state.get("api_key", "")
    api_base = st.session_state.get("api_base", "")

    if not api_key:
        yield "⚠️ 模型配置缺少 API Key"
        return

    if not api_base:
        yield "⚠️ 模型配置缺少 Base URL"
        return

    try:
        client = OpenAI(api_key=api_key, base_url=api_base)
    except Exception as e:
        yield f"⚠️ 创建客户端失败：{e}"
        return

    messages = convert_history_for_api(history, system_prompt, agent_name)

    try:
        stream = client.chat.completions.create(
            model=model_name, messages=messages, stream=True, temperature=temperature
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                # 防止 markdown 转义问题
                yield chunk.choices[0].delta.content.replace("~~", "\\~\\~")
    except Exception as e:
        yield f"⚠️ 请求出错：{e}"


for msg in st.session_state.messages:
    role = msg["role"]
    if role == "user":
        avatar = "👤"
    elif role == "researcher":
        avatar = "📚"
    elif role == "pm":
        avatar = "💼"
    else:
        continue
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("type your questions..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 如果当前对话标题还是默认的"新对话"，用用户第一条消息作为标题
    if st.session_state.current_title == "new chat" and len(prompt) > 0:
        st.session_state.current_title = prompt[:17] + (
            "..." if len(prompt) > 20 else ""
        )
        st.session_state.sessions[0].update_session_file(st.session_state.current_title)
        # update_current_session()

    # 研究员回复
    with st.chat_message("researcher", avatar="📚"):
        with st.spinner("the researcher is thinking..."):
            response1 = st.write_stream(
                stream_agent_response(
                    history=st.session_state.messages,
                    system_prompt=RESEARCHER_SYSTEM,
                    agent_name="researcher",
                    temperature=temperature,
                )
            )
    st.session_state.messages.append({"role": "researcher", "content": response1})

    # 产品经理回复
    with st.chat_message("pm", avatar="💼"):
        with st.spinner("产品经理正在思考方案..."):
            response2 = st.write_stream(
                stream_agent_response(
                    history=st.session_state.messages,
                    system_prompt=PM_SYSTEM,
                    agent_name="pm",
                    temperature=temperature,
                )
            )
    st.session_state.messages.append({"role": "pm", "content": response2})

    # 保存当前会话
    update_current_session()


available_models = model_helper.get_available_models()
default_model = list(available_models.keys())[0]

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


def styled_text(class_type: str, text_content: str, help_content: str = ""):
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
                        placeholder="editing new title...",
                    )
                else:
                    st.markdown(f"**{session.title}**")

            with col_edit:
                if st.session_state.editing_id == session.uuid:
                    if st.button("💾", help="save new title"):
                        new_title = st.session_state.get(
                            "new_title_buffer", session.title
                        )
                        session.update_session_file(new_title)
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
    display_models = {
        configs["display_name"]: model_name for model_name, configs in available_models.items()
        }

    current_display_name = available_models.get(
                            st.session_state.model_name, {}
                            ).get("display_name", st.session_state.model_name)

    selected_display_name = st.selectbox(
        "selecting model",
        options=list(display_models.keys()),
        index=(
            list(display_models.keys()).index(current_display_name)
            if current_display_name in display_models
            else 0
        ),
        help="choose from configs stated in secrets.toml",
    )

    selected_model_name = display_models[selected_display_name]
    selected_model_info = available_models[selected_model_name]
    st.session_state.model_name = selected_model_name
    st.session_state.api_key = selected_model_info["api_key"]
    st.session_state.api_base = selected_model_info["base_url"]
    st.success(f"current model: **{selected_display_name}**")

    st.markdown("### 🎛️ model parameters")
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, step=0.1)
