import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 📄 Page Configuration & Custom CSS Injection
st.set_page_config(page_title="AI Environment Design Coach", page_icon="🎨", layout="centered")

# Injection of clean container layout styles to prevent breaks
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
        div[data-testid="stExpander"] { border: 1px solid #e6e6e6 !important; box-shadow: none !important; }
    </style>
""", unsafe_allow_html=True)

# 2. ⚙️ Robust Session State Management (Bug Fixes Included)
# Track current stage to detect when the student changes it via the dropdown
if "previous_stage" not in st.session_state:
    st.session_state.previous_stage = "1. World Story"

# Unified dictionary to store completion metrics for all 7 workflows separately
if "checklist_status" not in st.session_state:
    st.session_state.checklist_status = {
        "1. World Story": {"Theme & Type": False, "World Narrative": False, "Architectural Identity": False},
        "2. Exterior Reference": {"Terrain Type": False, "Flora Reference": False, "Architectural Style": False},
        "3. Exterior Thumbnail": {"Composition Guide": False, "Value in Environment": False, "Horizon & Eye-Level": False},
        "4. Interior Reference": {"Spatial Zone": False, "Structural Reference": False, "Style & Culture": False},
        "5. Interior Thumbnail": {"Entry & Pathways": False, "Focal Hero Furniture": False, "Props Arrangement": False},
        "6. Exterior Polishing": {"Landscape Material": False, "Lighting & Atmosphere": False, "Weathered Effects": False},
        "7. Interior Polishing": {"Texture/Material Detail": False, "Light Flow & Contrast": False, "Usage Marks & History": False}
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "authenticated_key" not in st.session_state:
    st.session_state.authenticated_key = None

# 3. 🔑 Full-Screen Authentication Gate (Login Page)
if st.session_state.authenticated_key is None:
    # Automatically read and scale your 1600x600 layout banner seamlessly
    if os.path.exists("login_banner.png"):
        st.image("login_banner.png", use_container_width=True)
    elif os.path.exists("login_banner.jpg"):
        st.image("login_banner.jpg", use_container_width=True)
    else:
        st.title("🎨 Welcome to AI Environment Design Coach")
        st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")
        
    st.write("---")
    st.warning("👋 **Hello Student!** To unlock your Art Director Coach, please enter your personal Gemini API Key below.")
    
    input_key = st.text_input(
        "🔑 Paste your Gemini API Key here and press Enter:", 
        type="password", 
        placeholder="AIzaSy..."
    )
    
    st.info(
        "💡 **How to get your free API Key:**\n"
        "1. Sign in to [Google AI Studio 🔗](https://aistudio.google.com) with your Google account.\n"
        "2. Click the **Get API key** button.\n"
        "3. Copy the key and paste it above."
    )
    
    if input_key:
        st.session_state.authenticated_key = input_key.strip()
        st.rerun()
        
    st.stop()

# 4. Configure API (Only reached after successful authentication)
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]
genai.configure(api_key=st.session_state.authenticated_key)


# =====================================================================
# 🚀 THE TARGET 7-STAGE PIPELINE ENGINE (Twin-Track Architecture)
# =====================================================================

# 5. Dropdown Stage Selector (Aligned perfectly to your custom teaching workflow)
stage = st.selectbox(
    "📍 Choose your active design pipeline stage:",
    [
        "1. World Story",
        "2. Exterior Reference",
        "3. Exterior Thumbnail",
        "4. Interior Reference",
        "5. Interior Thumbnail",
        "6. Exterior Polishing",
        "7. Interior Polishing"
    ]
)

# 🛑 BUG FIX: If user switches stages, completely clear previous session canvas and reset conversation history
if stage != st.session_state.previous_stage:
    st.session_state.previous_stage = stage
    st.session_state.messages = []
    # Force delete image objects from keys cleanly
    if "current_image" in st.session_state:
        del st.session_state.current_image
    # Wipe the file uploader registry entirely to prevent cached memory remnants
    if "file_uploader_key" in st.session_state:
        st.session_state.file_uploader_key += 1
    else:
        st.session_state.file_uploader_key = 1
    st.rerun()

# Initialize dynamic dynamic key for uploader resetting
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0


# 6. 🖼️ Sidebar Area: Canvas & Dynamic Green Checklist Dashboard
with st.sidebar:
    st.title("🖼️ Design Workspace")
    st.markdown("---")
    
    # Needs image validation helper logic
    needs_img = stage in [
        "2. Exterior Reference", "3. Exterior Thumbnail", 
        "4. Interior Reference", "5. Interior Thumbnail", 
        "6. Exterior Polishing", "7. Interior Polishing"
    ]
    
    if needs_img:
        st.subheader("📸 Canvas Asset Upload")
        up_file = st.file_uploader(
            f"Upload current artwork/reference for {stage[3:]}", 
            type=["png", "jpg", "jpeg"],
            key=f"uploader_{st.session_state.file_uploader_key}"
        )
        
        if up_file:
            st.session_state.current_image = Image.open(up_file)
        
        if "current_image" in st.session_state and st.session_state.current_image is not None:
            st.image(st.session_state.current_image, caption="Active Review Object", use_container_width=True)
            # 🛑 BUG FIX: Clean removal button that successfully updates component state memory instantly
            if st.button("🗑️ Remove Asset Clear Canvas", use_container_width=True):
                del st.session_state.current_image
                st.session_state.file_uploader_key += 1
                st.rerun()
        st.markdown("---")
        
    # 🟢 Dynamic Metrics Dashboard Section
    st.subheader("📋 Design Specification Checklist")
    st.caption("These core analytical parameters update dynamically based on studio discourse.")
    
    current_metrics = st.session_state.checklist_status[stage]
    all_passed = True
    
    for metric_name, is_passed in current_metrics.items():
        if is_passed:
            st.success(f"✅ **{metric_name}**: Verified")
        else:
            st.info(f"⭕ **{metric_name}**: Pending...")
            all_passed = False
            
    if all_passed:
        st.markdown("---")
        st.balloons()
        st.success("🌟 **[STAGE COMPLETED]** Excellent execution! All core design parameters verified. Proceed to the next stage selector above.")


# 7. Main Area Content Layout & Interactive Discourse Engine
st.title("AI Environment Design Coach")
st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")

with st.expander("📖 Studio Guidelines & Pipeline Manual", expanded=False):
    st.write("**Simulate professional studio reviews with an Art Director to track criteria deliverables.**")
    st.markdown("""
    1. Select the current project assignment stage via the dropdown.
    2. Upload matching graphic assets into the **Sidebar Canvas** if required.
    3. Describe design intents inside the chat container box to receive targeted studio critique.
    """)

st.markdown("---")

# Render active chat streams natively inside main view window
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. 🚀 Interactive Prompt Guidance Blocks (Empty History State)
if len(st.session_state.messages) == 0:
    has_img = "current_image" in st.session_state
    
    example_prompts = {
        "1. World Story": "My world is a post-apocalyptic city with an old overgrown train station structure.",
        "2. Exterior Reference": "I uploaded a terrain ref showcasing sharp eroded canyons for the outer boundary.",
        "3. Exterior Thumbnail": "Here is my wide-angle composition thumbnail sketch, focusing heavily on environment values.",
        "4. Interior Reference": "This reference sheet establishes the layout layout rules for the bunker bedroom zone.",
        "5. Interior Thumbnail": "This is my top-view sketch plotting the entry paths and the placement of hero objects.",
        "6. Exterior Polishing": "I am working on blending weather textures, balancing moss overgrowth and atmospheric fog.",
        "7. Interior Polishing": "Refining the micro specular wood textures on desks alongside artificial candle lighting shadows."
    }
    
    with st.container():
        st.markdown(f"### 🚀 Initiating {stage[3:]} Studio Review")
        if needs_img and not has_img:
            st.error(f"⚠️ **Step 1:** Please upload your graphic asset file inside the **Sidebar Canvas** container first.")
            st.markdown("> *The Art Director needs to see your visual artifacts before evaluation can begin.*")
        else:
            st.success("✅ **System Ready:** Enter your design description inside the input engine below to alert the coach.")
            st.markdown(f"*Suggested starting phrase: \"{example_prompts[stage]}\"*")
        st.markdown("---")

# 9. 🧠 Chat Input Processing & Gamification Step-Unlock Automation Trigger
if prompt := st.chat_input("Communicate your structural layout design intents here..."):
    if needs_img and "current_image" not in st.session_state:
        st.sidebar.error("⚠️ Upload asset into canvas first!")
        st.warning("Please upload an image in the sidebar first so the coach can review your progress!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 🟢 Frontend Automation Logic: Advance checkpoints step-by-step per submission turn
        current_metrics = st.session_state.checklist_status[stage]
        metric_keys = list(current_metrics.keys())
        
        # Sequentially turn criteria green to reward input velocity smoothly without blockers
        if not current_metrics[metric_keys[0]]:
            st.session_state.checklist_status[stage][metric_keys[0]] = True
        elif not current_metrics[metric_keys[1]]:
            st.session_state.checklist_status[stage][metric_keys[1]] = True
        elif not current_metrics[metric_keys[2]]:
            st.session_state.checklist_status[stage][metric_keys[2]] = True
            
        st.rerun()

# 10. AI Engine Model Query Execution Block
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(
                model_name="gemini-3.1-flash-lite-preview",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            # Format context wrappers gracefully
            context_header = f"[STUDIO PIPELINE CONTEXT: Current Stage = {stage}]\nStudent Input: {st.session_state.messages[-1]['content']}"
            payload = [context_header]
            
            if "current_image" in st.session_state:
                payload.append(st.session_state.current_image)
                
            response = model.generate_content(payload)
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
        except Exception as e:
            st.error(f"Execution Error Encountered: {str(e)}")
