import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Environment Design Coach", page_icon="🎨", layout="centered")

# 2. Retrieve Configuration from Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]
genai.configure(api_key=API_KEY)

# 3. Sidebar: Canvas Area
with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")
    
    # Persistent Image Upload
    up_file = st.file_uploader("Upload your design or reference here", type=["png", "jpg", "jpeg"])
    st.caption("Mandatory for Reference, Thumbnail, and Polishing stages.")
    
    if up_file:
        st.session_state.current_image = Image.open(up_file)
    
    if "current_image" in st.session_state:
        st.image(st.session_state.current_image, caption="Current Review Object", use_container_width=True)
        if st.button("🗑️ Remove Image", use_container_width=True):
            if "current_image" in st.session_state:
                del st.session_state.current_image
            st.rerun()
    
    st.markdown("---")
    if st.button("🔄 Start New Critique", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.rerun()

# 4. Main Area: Header
st.title("Environment Design Coach")
st.markdown("#### AI Studio Critique for Environment Design Students")
st.info("**Key Idea:** AI-powered studio critique system that guides environment design thinking through structured questioning.")

with st.expander("📖 Guide & How to Start", expanded=False):
    st.write("**This tool simulates a studio critique with an art director.**")
    st.markdown("""
    1. Choose your **design stage**.
    2. Upload your image to the **Sidebar** (for Reference/Thumbnail/Polishing).
    3. Briefly describe your **intention** in the chat.
    """)

# 5. Stage Selector
stage = st.selectbox(
    "📍 Choose your design stage",
    ["Story", "Reference", "Thumbnail", "Polishing"]
)

st.markdown("---")

# 6. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Dynamic Starting Instructions (Optimized for Image + Text)
if len(st.session_state.messages) == 0:
    # Logic for image-based stages
    needs_image = stage in ["Reference", "Thumbnail", "Polishing"]
    
    example_text = {
        "Story": "My environment is an abandoned station in a cyberpunk city.",
        "Reference": "I've uploaded a reference for gothic lighting; I want to focus on the shadows.",
        "Thumbnail": "These are my 3 thumbnails for a forest temple; I'm comparing the focal points.",
        "Polishing": "I'm refining the textures and atmospheric fog for this night scene."
    }
    
    # Constructing the instruction box
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
        <p style="margin: 0; font-weight: bold; color: #31333F;">🚀 Starting {
