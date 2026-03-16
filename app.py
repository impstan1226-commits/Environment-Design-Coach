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
    
    # 优化清单 4：修改上传区域说明
    up_file = st.file_uploader("Upload your design, thumbnail, or reference image here", type=["png", "jpg", "jpeg"])
    st.caption("Recommended for Reference, Thumbnail, and Polishing stages.")
    
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

# 4. Main Area: Header & Key Idea
st.title("Environment Design Coach")
st.markdown("#### AI Studio Critique for Environment Design Students")

# 优化清单 5：保留 Key Idea
st.info("**Key Idea:** AI-powered studio critique system that guides environment design thinking through structured questioning.")

# 优化清单 1 & 2 & 6：修改介绍句、步骤顺序和 Guide 文字
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

# 7. Dynamic Starting Instructions
if len(st.session_state.messages) == 0:
    needs_image = stage in ["Reference", "Thumbnail", "Polishing"]
    
    # 优化清单 3：修改 Story 标题
    title_text = "🚀 Story Stage – Start Your World Concept" if stage == "Story" else f"🚀 Starting {stage} Stage"
    
    example_text = {
        "Story": "My environment is an abandoned station in a cyberpunk city.",
        "Reference": "I've uploaded a reference for gothic lighting; I want to focus on the shadows.",
        "Thumbnail": "These are my 3 thumbnails for a forest temple; I'm comparing the focal points.",
        "Polishing": "I'm refining the textures and atmospheric fog for this night scene."
    }
    
    with st.container():
        st.markdown(f"### {title_text}")
        
        # 按照逻辑，无论什么阶段，Step 1 都是说明意图
        st.markdown(f"**Step 1:** Briefly explain your intent in the chat box below.")
        
        if needs_image:
            # 如果是需要图的阶段，Step 2 提醒传图
            st.warning("⚠️ **Step 2:** Upload your image in the **Sidebar** to help the coach see your work.")
        
        st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
        st.markdown("---")

# 8. Chat Input & Logic
if prompt := st.chat_input("Describe your concept here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
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
        st.error(f"Error: {str(e)}")
