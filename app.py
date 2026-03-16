import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Environment Design Coach", page_icon="🎨", layout="centered")

# 2. Retrieve Configuration from Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]
genai.configure(api_key=API_KEY)

# 3. Sidebar: Canvas & Control Area
with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")
    
    # Image Upload
    up_file = st.file_uploader("Upload your design or reference here", type=["png", "jpg", "jpeg"])
    st.caption("Use this to upload thumbnails, references, or work-in-progress images.")
    
    if up_file:
        st.session_state.current_image = Image.open(up_file)
    
    if "current_image" in st.session_state:
        st.image(st.session_state.current_image, caption="Current Review Object", use_container_width=True)
        if st.button("🗑️ Remove Image", use_container_width=True):
            if "current_image" in st.session_state:
                del st.session_state.current_image
            st.rerun()
    
    st.markdown("---")
    # Reset Button with Professional Label
    if st.button("🔄 Start New Critique", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.rerun()

# 4. Main Area: Header & Key Idea
st.title("Environment Design Coach")
st.markdown("#### AI Studio Critique for Environment Design Students")

st.info("**Key Idea:** AI-powered studio critique system that guides environment design thinking through structured questioning.")

# 5. Guide & Stage Selector
with st.expander("📖 Guide & How to Start", expanded=True):
    st.write("**This tool simulates a studio critique with an art director.** Describe your environment idea or upload an image. The coach will guide you with short questions.")
    st.markdown("""
    1. Choose your **design stage**.
    2. Briefly describe your **idea**.
    3. Upload an **image** to the sidebar if needed.
    """)

stage = st.selectbox(
    "📍 Choose your design stage",
    ["Story", "Reference", "Thumbnail", "Polishing"]
)

st.markdown("---")

# 6. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Dynamic Example Prompt (Only shows before chat starts)
if len(st.session_state.messages) == 0:
    # Logic to change examples based on the selected stage
    examples = {
        "Story": "My environment is an abandoned station in a cyberpunk city.",
        "Reference": "I've uploaded a reference of a gothic cathedral for its lighting.",
        "Thumbnail": "This is a thumbnail for a forest temple scene focusing on the entrance.",
        "Polishing": "I'm refining the atmosphere for this desert camp at night."
    }
    
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
        <p style="margin: 0; font-weight: bold; color: #31333F;">💡 How to start in {stage} stage:</p>
        <p style="margin: 5px 0 0 0; font-style: italic; color: #555;">
            Try saying: "{examples[stage]}"
        </p>
    </div>
    """, unsafe_allow_html=True)

# 8. Chat Input & AI Logic
if prompt := st.chat_input("Describe your concept here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Context Injection
        context_prompt = f"[CONTEXT: Design Stage = {stage}]\nStudent Input: {prompt}"
        
        # Use the specific model confirmed previously
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
            else:
                st.error("The AI could not generate a response.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
