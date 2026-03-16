import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Environment Design Coach", page_icon="🎨", layout="wide")

# 2. Retrieve Configuration from Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]

# Configure Gemini API
genai.configure(api_key=API_KEY)

# 3. Sidebar: Persistent Image Display
with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")
    
    up_file = st.file_uploader("Upload your design/reference here", type=["png", "jpg", "jpeg"])
    
    if up_file:
        st.session_state.current_image = Image.open(up_file)
    
    if "current_image" in st.session_state:
        st.image(st.session_state.current_image, caption="Current Review Object", use_container_width=True)
        if st.button("🗑️ Remove Image", use_container_width=True):
            del st.session_state.current_image
            st.rerun()
    else:
        st.info("No image uploaded yet.")
    
    st.markdown("---")
    if st.button("🔄 Reset Full Chat", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.rerun()

# 4. Main Area: Header
st.title("🎨 Environment Design Coach")
st.markdown("##### AI-Powered Studio Critique for Environment Design Students")

with st.expander("📖 How to Start & User Guide"):
    st.write("""
    This tool simulates a Studio Critique. The coach will guide you through short questions to clarify your design thinking.
    1. Select your **Design Phase**.
    2. Describe your concept.
    3. Upload an image to the **Sidebar** if needed.
    """)

# 5. Phase Selector
phase = st.selectbox(
    "📍 Select your design phase",
    ["Story", "Reference", "Thumbnail", "Polishing"]
)

# 6. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Example Prompts (修复了这里的引号逻辑)
st.info("Example: 'My environment is an abandoned station in a cyberpunk city.'")

# 8. Chat Input Logic
if prompt := st.chat_input("Describe your concept here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        context_prompt = f"[CONTEXT: Design Phase = {phase}]\nStudent Input: {prompt}"
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        with st.chat_message("assistant"):
            parts = [context_prompt]
            if "current_image" in st.session_state:
                parts.append(st.session_state.current_image)
            
            response = model.generate_content(parts)
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
