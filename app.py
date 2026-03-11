import streamlit as st
import google.generativeai as genai
from PIL import Image

# 从 Streamlit 的加密后台读取 API Key 和指令
API_KEY = st.secrets["GEMINI_API_KEY"]
MY_INSTRUCTION = st.secrets["COMMAND_CENTER"]

genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Environment Design Coach")
st.title("🎨 Environment Design Coach")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

up_file = st.file_uploader("Upload design", type=["png", "jpg", "jpeg"])

if prompt := st.chat_input("Explain your work..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 这里的 instruction 也是加密读取的
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=MY_INSTRUCTION)
    
    with st.chat_message("assistant"):
        parts = [prompt]
        if up_file:
            parts.append(Image.open(up_file))
        response = model.generate_content(parts)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
