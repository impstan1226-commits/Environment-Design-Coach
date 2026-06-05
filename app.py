import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Configuration
st.set_page_config(page_title="AI Environment Design Coach", page_icon="🎨", layout="centered")

# 2. Advanced Session State Memory Management (Bug Fix: Full Reset Integrity)
if "authenticated_key" not in st.session_state:
    st.session_state.authenticated_key = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Specifications Database: Dynamic Text summaries extracted from the AI tokens live
if "spec_summaries" not in st.session_state:
    st.session_state.spec_summaries = {
        "1. World Story": {"Theme & Type": None, "World Narrative": None, "Architectural Identity": None},
        "2. Exterior Reference": {"Terrain Type": None, "Flora Reference": None, "Architectural Style": None},
        "3. Exterior Thumbnail": {"Composition Guide": None, "Value in Environment": None, "Horizon & Eye-Level": None},
        "4. Interior Reference": {"Spatial Zone": None, "Structural Reference": None, "Style & Culture": None},
        "5. Interior Thumbnail": {"Entry & Pathways": None, "Focal Hero Furniture": None, "Props Arrangement": None},
        "6. Exterior Polishing": {"Landscape Material": None, "Lighting & Atmosphere": None, "Weathered Effects": None},
        "7. Interior Polishing": {"Texture/Material Detail": None, "Light Flow & Contrast": None, "Usage Marks & History": None}
    }

# Rolling paragraph description to continuously accumulate and improve narrative context
if "rolling_story_summary" not in st.session_state:
    st.session_state.rolling_story_summary = ""

# 3. 🔑 Full-Screen Authentication Gate (Login Page)
if st.session_state.authenticated_key is None:
    if os.path.exists("login_banner.png"):
        st.image("login_banner.png", use_container_width=True)
    elif os.path.exists("login_banner.jpg"):
        st.image("login_banner.jpg", use_container_width=True)
    else:
        st.title("🎨 Welcome to AI Environment Design Coach")
        st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")
        
    st.write("---")
    st.warning("👋 **Hello Student!** To unlock your AI EDC Art Director Coach, please enter your personal Gemini API Key below.")
    
    input_key = st.text_input("🔑 Paste your Gemini API Key here and press Enter:", type="password", placeholder="AIzaSy...")
    
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

# 4. Configure API
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]
genai.configure(api_key=st.session_state.authenticated_key)


# =====================================================================
# 🚀 CLASSROOM DISCOURSE ENGINE Layout
# =====================================================================

# Dynamic key system used to completely break file uploader cache blocks on switch actions
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

# Dynamic selector routing index logic
stage_options = [
    "1. World Story", "2. Exterior Reference", "3. Exterior Thumbnail",
    "4. Interior Reference", "5. Interior Thumbnail", "6. Exterior Polishing", "7. Interior Polishing"
]

if "stage_index_memory" not in st.session_state:
    st.session_state.stage_index_memory = 0

# 6. 🖼️ Sidebar Panel: Canvas Setup & Cumulative Specifications Tracker
with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")
    
    # Check current staging parameters
    current_selected_stage = stage_options[st.session_state.stage_index_memory]
    needs_img = current_selected_stage != "1. World Story"
    
    if needs_img:
        up_file = st.file_uploader(
            "Upload your design, thumbnail, or reference image here", 
            type=["png", "jpg", "jpeg"],
            key=f"uploader_{st.session_state.file_uploader_key}"
        )
        st.caption("Mandatory for Reference, Thumbnail, and Polishing stages.")
        
        if up_file:
            st.session_state.current_image = Image.open(up_file)
        
        if "current_image" in st.session_state and st.session_state.current_image is not None:
            st.image(st.session_state.current_image, caption="Current Review Object", use_container_width=True)
            if st.button("🗑️ Remove Image", use_container_width=True):
                del st.session_state.current_image
                st.session_state.file_uploader_key += 1
                st.rerun()
        st.markdown("---")
        
    # 📋 Dynamic Dashboard Checklist (Accumulative Patch Engine)
    st.subheader("📋 Design Specification")
    st.caption("This board auto-updates and accumulates information permanently as you design.")
    
    active_specs = st.session_state.spec_summaries[current_selected_stage]
    
    for metric, text_summary in active_specs.items():
        if text_summary and text_summary.strip().lower() != "none" and text_summary.strip() != "":
            st.success(f"✅ **{metric}**:\n{text_summary}")
        else:
            st.info(f"⭕ **{metric}**:\n*Pending feedback...*")
            
    # 📝 核心升级：增加全局故事积累摘要文字框
    if current_selected_stage == "1. World Story":
        st.markdown("---")
        st.subheader("📝 World Concept Summary")
        if st.session_state.rolling_story_summary:
            st.info(st.session_state.rolling_story_summary)
        else:
            st.caption("*Story narrative summary will build up here progressively based on your studio review discussion...*")

    st.markdown("---")
    
    # 🔄 BUG FIX 4: Complete system deep flash wipe logic
    if st.button("🔄 Start New Critique", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.session_state.file_uploader_key += 1
        st.session_state.stage_index_memory = 0  # Force jump back to stage 1
        st.session_state.rolling_story_summary = ""  # Clear narrative memory
        # Flush the spec summaries database entirely to clear persistent green marks
        st.session_state.spec_summaries = {
            k: {sub_k: None for sub_k in v} for k, v in st.session_state.spec_summaries.items()
        }
        st.rerun()
        
    if st.button("🚪 Disconnect API Key", use_container_width=True):
        st.session_state.authenticated_key = None
        st.rerun()


# 7. Main Area Content Rendering
st.title("AI Environment Design Coach")
st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")
st.info("**AI EDC Hint:** Talk with the studio Art Director to refine your Environment Art Bible requirements.")

with st.expander("📖 How to Start & User Guide", expanded=False):
    st.write("**This tool simulates a studio critique with an art director to guide environment design thinking.**")
    st.markdown("""
    1. Choose your **design stage**.
    2. Briefly describe your **idea** in the chat.
    3. Upload an **image** if needed (for Reference, Thumbnail, or Polishing stages).
    """)

# BUG FIX 1: Reposition the Selector Node neatly inside the core document flow below the Guide panel
stage = st.selectbox(
    "🔑 Choose your active pipeline design assignment stage:",
    stage_options,
    index=st.session_state.stage_index_memory
)

# Detect if the index was triggered manually to handle state change safety
if stage != stage_options[st.session_state.stage_index_memory]:
    st.session_state.stage_index_memory = stage_options.index(stage)
    st.session_state.messages = []
    if "current_image" in st.session_state:
        del st.session_state.current_image
    st.session_state.file_uploader_key += 1
    st.rerun()

st.markdown("---")

# Render active discourse window blocks
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Render classic guide parameters on fresh arrays
if len(st.session_state.messages) == 0:
    has_img = "current_image" in st.session_state
    
    example_text = {
        "1. World Story": "My environment is an abandoned station in a cyberpunk city.",
        "2. Exterior Reference": "I've uploaded a reference for sharp gothic canyons; I want to focus on the cliff rock shapes.",
        "3. Exterior Thumbnail": "These are my wide-angle thumbnail layout sketches; I'm comparing the depth of three planes.",
        "4. Interior Reference": "I've uploaded reference images for an industrial bunker control room layout.",
        "5. Interior Thumbnail": "This is my top-view schematic mapping out the doorways and the central hero prop table.",
        "6. Exterior Polishing": "I'm refining the moss blending textures and adjusting the distance atmospheric fog layers.",
        "7. Interior Polishing": "I am painting the micro specular highlights on desks matching single window cool moonlight rays."
    }

    with st.container():
        st.markdown(f"### 🚀 Starting {stage[3:]} Stage")
        if needs_img:
            if not has_img:
                st.error("⚠️ **Step 1:** Please upload your image in the **Sidebar Design Canvas** first.")
                st.markdown("> *Wait for the coach to see your work before describing it.*")
            else:
                st.success("✅ **Step 1 Complete:** Image uploaded successfully.")
                st.markdown(f"**Step 2:** Briefly explain your design intent in the chat box below.")
                st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
        else:
            st.markdown(f"**Step 1:** Briefly explain your world concept in the chat box below.")
            st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
        st.markdown("---")

# 9. Handle Chat Inputs
if prompt := st.chat_input("Describe your environment concepts here..."):
    if needs_img and "current_image" not in st.session_state:
        st.warning("Please upload an image in the sidebar canvas first so the coach can review it!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# 10. Core AI Thread Generation and Multi-Token Interception Layer
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(
                model_name="gemini-3.1-flash-lite-preview",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            # Formulate robust history parameters to stop context drift bugs entirely
            payload = [f"[PIPELINE ASSIGNMENT ZONE: {stage}]"]
            if st.session_state.rolling_story_summary:
                payload.append(f"[CURRENT VERIFIED STORY SUMMARY PROGRESS: {st.session_state.rolling_story_summary}]")
                
            payload.append(f"Student Input: {st.session_state.messages[-1]['content']}")
            if "current_image" in st.session_state:
                payload.append(st.session_state.current_image)
                
            response = model.generate_content(payload)
            raw_text = response.text if response.text else ""
            
            display_text = raw_text
            
            # Extract meta parameters safely via split strings
            if "[SUMMARY:" in raw_text:
                parts_split = raw_text.split("[SUMMARY:", 1)
                display_text = parts_split[0].strip()
                meta_block = parts_split[1].split("]", 1)[0].strip()
                
                pairs = meta_block.split("|")
                for pair in pairs:
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        k_clean = k.strip()
                        v_clean = v.strip()
                        
                        # BUG FIX 2: Accumulative lock. Only overwrite if the AI gives actual data, never replace with None!
                        if k_clean in st.session_state.spec_summaries[stage]:
                            if v_clean.lower() != "none" and v_clean != "":
                                st.session_state.spec_summaries[stage][k_clean] = v_clean
                                
            # 🔍 Extract Narrative Snowball parameters safely
            if "[STORY_BOX:" in raw_text:
                story_parts = raw_text.split("[STORY_BOX:", 1)
                if not "[SUMMARY:" in story_parts[0]: # Clean up text rendering safety
                    display_text = story_parts[0].strip()
                story_content = story_parts[1].split("]", 1)[0].strip()
                if story_content.lower() != "none" and story_content != "":
                    st.session_state.rolling_story_summary = story_content

            st.markdown(display_text)
            st.session_state.messages.append({"role": "assistant", "content": display_text})
            st.rerun()
            
        except Exception as e:
            st.error(f"Engine Core Exception Error: {str(e)}")
