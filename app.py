import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="AI Environment Design Coach", page_icon="🎨", layout="centered")

# 2. Configure API (System Instruction from Secrets)
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]

# 3. Sidebar: Canvas & API Key Area
with st.sidebar:
    st.title("🔑 Student Authentication")
    student_key = st.text_input(
        "Enter your Gemini API Key:", 
        type="password", 
        placeholder="AIzaSy...",
        help="Get your free API Key from https://aistudio.google.com"
    )
    st.markdown("[Get Free Gemini API Key 🔗](https://aistudio.google.com)")
    st.markdown("---")
    
    st.title("🖼️ Design Canvas")
    
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

# 3.5 API Verification Interceptor
if not student_key:
    st.title("AI Environment Design Coach")
    st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")
    st.warning("👋 **Welcome, Student!** Please grab your free Gemini API Key from **Google AI Studio** and paste it into the sidebar on the left to unlock your Art Director Coach.")
    st.info("💡 **Quick Guide:**\n1. Sign in to [Google AI Studio](https://aistudio.google.com) with your Google account.\n2. Click **Create API Key**.\n3. Copy the key and paste it into the **Student Authentication** box on the left.")
    st.stop()  # Stop executing the rest of the script until the key is provided
else:
    # Configure the API with the student's personal key
    genai.configure(api_key=student_key)

# 4. Main Area: Header
st.title("AI Environment Design Coach")
st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")
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

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. 🚀 重新找回的动态引导步骤 (Starting Stage Section)
if len(st.session_state.messages) == 0:
    has_img = "current_image" in st.session_state
    needs_img = stage in ["Reference", "Thumbnail", "Polishing"]
    
    example_text = {
        "Story": "My environment is an abandoned station in a cyberpunk city.",
        "Reference": "I've uploaded a reference for gothic lighting; I want to focus on the shadows.",
        "Thumbnail": "These are my 3 thumbnails for a forest temple; I'm comparing the focal points.",
        "Polishing": "I'm refining the textures and atmospheric fog for this night scene."
    }

    # 使用 Streamlit 原生 container 模拟之前的视觉效果
    with st.container():
        header_title = "🚀 Story Stage – Start Your World Concept" if stage == "Story" else f"🚀 Starting {stage} Stage"
        st.markdown(f"### {header_title}")

        if needs_img:
            if not has_img:
                st.error("⚠️ **Step 1:** Please upload your image in the **Sidebar** first.")
                st.markdown("> *Wait for the coach to see your work before describing it.*")
            else:
                st.success("✅ **Step 1 Complete:** Image uploaded.")
                st.markdown(f"**Step 2:** Briefly explain your intent in the chat box below.")
                st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
        else:
            st.markdown(f"**Step 1:** Briefly explain your world concept in the chat box below.")
            st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
        
        st.markdown("---")

# 8. Chat Input & AI Logic
if prompt := st.chat_input("Describe your concept here..."):
    if stage in ["Reference", "Thumbnail", "Polishing"] and "current_image" not in st.session_state:
        st.warning("Please upload an image in the sidebar first so the coach can review it!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(
                model_name="gemini-3.1-flash-lite-preview", 
                system_instruction=SYSTEM_INSTRUCTION
            )
            parts = [f"[CONTEXT: Design Stage = {stage}]\nStudent Input: {st.session_state.messages[-1]['content']}"]
            if "current_image" in st.session_state:
                parts.append(st.session_state.current_image)
            
            response = model.generate_content(parts)
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
