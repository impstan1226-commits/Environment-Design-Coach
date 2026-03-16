import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Environment Design Coach", page_icon="🎨", layout="wide")

# 2. Secrets & API
API_KEY = st.secrets["GEMINI_API_KEY"]
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]
genai.configure(api_key=API_KEY)

# 3. Sidebar: Canvas & Examples
with st.sidebar:
    st.title("🖼️ Design Canvas")
    up_file = st.file_uploader("Upload your work", type=["png", "jpg", "jpeg"])
    if up_file:
        st.session_state.current_image = Image.open(up_file)
    
    if "current_image" in st.session_state:
        st.image(st.session_state.current_image, use_container_width=True)
        if st.button("🗑️ Remove Image"):
            del st.session_state.current_image
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    **Example inputs to try:**
    - *"My environment is an abandoned station in a cyberpunk city."*
    - *"This is a thumbnail for a forest temple scene."*
    """)
    
    if st.button("🔄 Start New Critique", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.rerun()

# 4. Main Area
st.title("Environment Design Coach")
st.info("**Key Idea:** AI-powered studio critique system that guides design thinking through structured questioning.")

stage = st.selectbox("📍 Choose your design stage", ["Story", "Reference", "Thumbnail", "Polishing"])

# Chat Display
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Input
if prompt := st.chat_input("Describe your concept here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Use the correct model name you specified
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite-preview", 
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        context_prompt = f"[CONTEXT: Stage={stage}]\nStudent: {prompt}"
        
        with st.chat_message("assistant"):
            parts = [context_prompt]
            if "current_image" in st.session_state:
                parts.append(st.session_state.current_image)
            
            response = model.generate_content(parts)
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Error: {str(e)}")
