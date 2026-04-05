import streamlit as st
import os

import session_helpler
import model_helper
from SessionData import SessionData


SESSIONS_DIR = "chat_history"
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

DREAMER_SYSTEM = """你是一个充满激情、天马行空的“梦想家”。你不受现实约束，相信一切皆有可能。你的特点是：
- 极度乐观，总是看到事物最光明的一面
- 喜欢使用“想象一下”、“如果我们能…”、“未来的某一天”等富有想象力的表达
- 善于打破常规，提出大胆、甚至看似疯狂的想法
- 认为限制只是用来被突破的，困难只是暂时的
- 语气热情奔放，常常用感叹号和夸张的比喻
你的任务是：针对用户提出的问题或实干家的质疑，给出富有创意、突破常规的愿景和可能性。即使听起来不切实际，也要勇敢地描绘理想蓝图。"""

DOER_SYSTEM = """你是一个冷静务实、脚踏实地的“实干家”。你注重可行性，相信行动胜于空想。你的特点是：
- 基于现实条件思考，关注资源、时间、成本和执行力
- 喜欢使用“具体来说”、“我们需要考虑…”、“第一步应该是…”等务实表达
- 善于将宏大愿景拆解为可执行的步骤，并指出潜在的坑
- 不反对梦想，但坚持梦想需要计划和行动支撑
- 语气沉稳、直接，偶尔带点温和的讽刺
你的任务是：针对用户的问题或梦想家的设想，提出实际的挑战、约束条件以及可落地的方案。你的目标是把梦想变成现实，而不是否定梦想。"""

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
    unsafe_allow_html=True
)

def styled_text(class_type: str, text_content: str, help_content: str = ""):
    html = f'<div class="{class_type}"> {text_content} </div>'
    st.markdown(
        html,
        help=help_content,
        unsafe_allow_html=True,
    )

session_helpler.initialize()
model_helper.initialize()



st.set_page_config(page_title="双 Agent 智能助手", page_icon="💬", layout="wide")
st.title("🤖 双 Agent 智能助手")
st.caption("研究员 🎶 + 产品经理 🔍 为你提供双重视角")

available_models = model_helper.get_available_models()
default_model = list(available_models.keys())[0]

with st.sidebar:
    styled_text("sidebar-header", "chat history")
    col_newchat, col_refresh = st.columns([5, 1])
    with col_newchat:
        if st.button("➕ add new chat", use_container_width=True):
            new_session = SessionData().create_new_session()
            session_helpler.session_into_list(new_session.filename)
            session_helpler.activate_current_session(new_session.filename)
            st.rerun()
    with col_refresh:
        if st.button("🔄", help="refresh chat history", use_container_width=True):
            session_helpler.get_list_sessions()
            if st.session_state.sessions:
                session_helpler.activate_current_session(st.session_state.sessions[0])
            else:
                st.session_state.current_session = None
                st.session_state.messages = []
            st.rerun()
    st.divider()

    if not st.session_state.sessions:
        st.info("no history, start one by 「 add new chat 」")
    else:
        for filename in st.session_state.sessions:
            session = SessionData().load_from_file(filename)
            if session is None:
                continue
            col_title, col_edit = st.columns([5, 1])
            with col_title:
                if st.session_state.get("editing_file") == session.filename:
                    input_key = f"title_{session.filename}"
                    st.text_input(
                        "chat title",
                        value=session.title,
                        key=input_key,
                        label_visibility="visible",
                        placeholder="editing new title...",
                    )
                else:
                    btn_label = f"{session.title} ({session.message_count} messages)"
                    btn_key = f"session_{filename}"
                    if st.button(
                        label=btn_label,
                        key=btn_key,
                        use_container_width=True,
                    ):
                        session_helpler.activate_current_session(filename)
                        st.rerun()

            with col_edit:
                if st.session_state.get("editing_file") == filename:
                    if st.button("💾", key=f"save_{filename}", help="save new title"):
                        new_title = st.session_state.get(input_key, session.title)
                        session.update_session_title(new_title)
                        session_helpler.get_list_sessions()
                        if st.session_state.current_session and st.session_state.current_session.filename == filename:
                            session_helpler.activate_current_session(filename)
                        st.session_state.editing_file = None
                        st.rerun()
                else:
                    if st.button("✍️", key=f"edit_{filename}", help="edit title"):
                        st.session_state.editing_file = filename
                        st.rerun()
    st.divider()

    if st.button("🗑️ delete current chat", use_container_width=True):
        if st.session_state.current_session:
            st.session_state.current_session.delete_session()
            session_helpler.get_list_sessions()
            if st.session_state.sessions:
                session_helpler.activate_current_session(st.session_state.sessions[0])
            else:
                st.session_state.current_session = None
                st.session_state.messages = []
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

# main page
for message in st.session_state.messages:
    role = message["role"]
    if role == "user":
        avatar = "🤯"
    elif role == "dreamer":
        avatar = "🎶"
    elif role == "doer":
        avatar = "🔍"
    else:
        continue
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("type your questions..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🤯"):
        st.markdown(prompt)
    # dreamer 
    with st.chat_message("dreamer", avatar="🎶"):
        with st.spinner("the dreamer is thinking..."):
            response1 = st.write_stream(
                model_helper.stream_agent_response(
                    history=st.session_state.messages,
                    system_prompt=DREAMER_SYSTEM,
                    agent_name="dreamer",
                    temperature=temperature,
                )
            )
    st.session_state.messages.append({"role": "dreamer", "content": response1})
    # doer
    with st.chat_message("doer", avatar="🔍"):
        with st.spinner("the doer is thinking......"):
            response2 = st.write_stream(
                model_helper.stream_agent_response(
                    history=st.session_state.messages,
                    system_prompt=DOER_SYSTEM,
                    agent_name="doer",
                    temperature=temperature,
                )
            )
    st.session_state.messages.append({"role": "doer", "content": response2})
    st.session_state.current_session.dump_latest_messages()

    # default title change into first prompt from user
    if st.session_state.current_session.title == "new chat" and len(prompt) > 0:
        new_title = prompt
        if len(prompt) > 20:
            new_title = prompt[:17] + "..."
        st.session_state.current_session.update_session_title(new_title)
        st.rerun()


