import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration - Back to standard layout for stability
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
    up_file = st.file_uploader("Upload your design/reference", type=["png", "jpg", "jpeg"])
    if up_file:
        st.session_state.current_image = Image.open(up_file)
    
    if "current_image" in st.session_state:
        st.image(st.session_state.current_image, caption="Current Review Object", use_container_width=True)
        if st.button("🗑️ Remove Image", use_container_width=True):
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

# 4. Main Area: Structured Layout
st.title("Environment Design Coach")
st.markdown("#### AI Studio Critique for Environment Design Students")

# Key Idea Box
st.info("**Key Idea:** AI-powered studio critique system that guides environment design thinking through structured questioning.")

# Guide (Ensuring it shows up properly)
with st.expander("📖 Guide & How to Start", expanded=True):
    st.write("**This tool simulates a studio critique with an art director.**")
    st.markdown("""
    1. Choose your **design stage**.
    2. Briefly describe your **idea**.
    3. Upload an **image** to the sidebar if needed.
    """)

# Stage Selector
stage = st.selectbox(
    "📍 Choose your design stage",
    ["Story", "Reference", "Thumbnail", "Polishing"]
)

st.markdown("---")

# 5. Chat History Display
if "messages" not in st.session_state:
    st.session_state.messages = []

# Using a container to keep chat messages organized
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 6. Chat Input Logic
if prompt := st.chat_input("Describe your concept here..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Context Injection
        context_prompt = f"[CONTEXT: Design Stage = {stage}]\nStudent Input: {prompt}"
        
        # Initialize Model (Correct version)
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite-preview", 
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        with st.chat_message("assistant"):
            parts = [context_prompt]
            if "current_image" in st.session_state:
                parts.append(st.session_state.current_image)
            
            # Generate Response
            response = model.generate_content(parts)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.error("The AI could not generate a response.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
