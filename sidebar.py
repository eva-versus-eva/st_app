import streamlit as st
from langchain_openai.chat_models import ChatOpenAI

st.title("🦜🔗 Quickstart App")

openai_api_key = st.sidebar.text_input("DEEPSEEK API Key", type="password")


def generate_response(input_text):
    model = ChatOpenAI(
        temperature=0.7,
        api_key=openai_api_key,
        model="deepseek-chat",
        base_url="https://api.deepseek.com/",
    )
    st.info(model.invoke(input_text).content)


with st.form("my_form"):
    text = st.text_area(
        "Enter text:",
        "What are the three key pieces of advice for learning how to code?",
    )
    submitted = st.form_submit_button("Submit")
    if not openai_api_key:
        st.warning("Please enter your DeepSeek API key!", icon="⚠")
    if submitted and openai_api_key:
        generate_response(text)
