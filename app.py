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

# 3. Sidebar: Canvas Area (Requirement #5 & #6)
with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")
    
    # Upload with small hint text
    up_file = st.file_uploader("Upload your design or reference image here", type=["png", "jpg", "jpeg"])
    st.caption("Use this to upload thumbnails, references, or work-in-progress images.")
    
    if up_file:
        st.session_state.current_image = Image.open(up_file)
    
    if "current_image" in st.session_state:
        st.image(st.session_state.current_image, caption="Current Review Object", use_container_width=True)
        if st.button("🗑️ Remove Image", use_container_width=True):
            del st.session_state.current_image
            st.rerun()
    
    st.markdown("---")
    # Updated Reset Button Label (Requirement #6)
    if st.button("🔄 Start New Critique", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.rerun()

# 4. Main Area: Header & Introduction (Requirement #1, #2, #7)
st.title("Environment Design Coach")
st.markdown("#### AI Studio Critique for Environment Design Students")
st.info("**Key Idea:** AI-powered studio critique system that guides environment design thinking through structured questioning.")

with st.expander("📖 Guide & How to Start", expanded=True):
    st.write("**This tool simulates a studio critique with an art director.** Describe your environment idea or upload an image. The coach will guide you with short questions to help clarify your design thinking.")
    st.markdown("""
    **How to Start:**
    1. Select your **design stage**.
    2. Briefly describe your **idea**.
    3. Upload an **image** if needed.
    """)

# 5. Stage Selector (Requirement #3)
stage = st.selectbox(
    "📍 Choose your design stage",
    ["Story", "Reference", "Thumbnail", "Polishing"]
)

# 6. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Example Inputs (Requirement #4)
st.markdown("""
<p style='color: #888; font-size: 0.85rem;'>
<b>Example inputs:</b><br>
- "My environment is an abandoned station in a cyberpunk city."<br>
- "This is a thumbnail for a forest temple scene."
</p>
""", unsafe_allow_html=True)

# 8. Chat Input Logic
if prompt := st.chat_input("Describe your concept here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Context includes the 'Stage' instead of 'Phase'
        context_prompt = f"[CONTEXT: Design Stage = {stage}]\nStudent Input: {prompt}"
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite-preview", 
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
