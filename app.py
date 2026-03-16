import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="AI Environment Design Coach", page_icon="🎨", layout="centered")

# 2. Configure API
API_KEY = st.secrets["GEMINI_API_KEY"]
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]
genai.configure(api_key=API_KEY)

# 3. Sidebar: Canvas Area
with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")
    
    # 修改上传说明
    up_file = st.file_uploader("Upload your design, thumbnail, or reference image here", type=["png", "jpg", "jpeg"])
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

# 4. Main Area: Header (优化清单：修改标题与副标题)
st.title("AI Environment Design Coach")
st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")

# Key Idea 区块保持不变
st.info("**Key Idea:** AI-powered studio critique system that guides environment design thinking through structured questioning.")

with st.expander("📖 How to Start & User Guide", expanded=True):
    st.write("**This tool simulates a studio critique with an art director to guide environment design thinking.**")
    st.markdown("""
    1. Choose your **design stage**.
    2. Briefly describe your **idea** in the chat.
    3. Upload an **image** if needed (for Reference, Thumbnail, or Polishing stages).
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

# 7. Dynamic Starting Instructions (保持之前的优化逻辑)
if len(st.session_state.messages) == 0:
    has_img = "current_image" in st.session_state
    needs_img = stage in ["Reference", "Thumbnail", "Polishing"]
