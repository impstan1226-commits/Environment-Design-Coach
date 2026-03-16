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

# 3. Sidebar: Persistent Image Display (Requirement #10 & Visual Thinking)
with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")
    
    # Image Uploader
    up_file = st.file_uploader("Upload your design/reference here", type=["png", "jpg", "jpeg"])
    
    # Persistent storage logic for the image
    if up_file:
        st.session_state.current_image = Image.open(up_file)
    
    # Show the image if it exists in session
    if "current_image" in st.session_state:
        st.image(st.session_state.current_image, caption="Current Review Object", use_container_width=True)
        if st.button("🗑️ Remove Image", use_container_width=True):
            if "current_image" in st.session_state:
                del st.session_state.current_image
            st.rerun()
    else:
        st.info("No image uploaded yet. You can still discuss your concept via text.")
    
    st.markdown("---")
    if st.button("🔄 Reset Full Chat", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.rerun()

# 4. Main Area: Header & Introduction (Requirement #1)
st.title("🎨 Environment Design Coach")
st.markdown("##### AI-Powered Studio Critique for Environment Design Students")

with st.expander("📖 How to Start & User Guide", expanded=False):
    st.write("""
    This tool simulates a **Studio Critique** with an Art Director. The coach will guide you through short, targeted questions to help clarify your design thinking.
    
    **Instructions:**
    1. Select your current **Design Phase** below.
    2. Briefly describe your concept or environment.
    3. Upload an image to the **Sidebar** if needed.
    4. The coach will prompt you with a design question.
    
    **Tip:** There are no "right" answers. You are the designer; the coach is here to help you think deeper.
    """)

# 5. Phase Selector (Requirement #2)
phase = st.selectbox(
    "📍 Select your design phase",
    ["Story", "Reference", "Thumbnail", "Polishing"],
    help="The coach will tailor questions based on your selected phase."
)

# 6. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History (Requirement #7)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Example Prompts (Requirement #3)
st.markdown("""
