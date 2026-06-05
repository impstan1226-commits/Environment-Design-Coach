import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Configuration
st.set_page_config(page_title="AI Environment Design Coach", page_icon="🎨", layout="centered")

# 2. Initialize Session State (Bug Fixes: Save Key independently from clear actions)
if "authenticated_key" not in st.session_state:
    st.session_state.authenticated_key = None

if "previous_stage" not in st.session_state:
    st.session_state.previous_stage = "1. World Story"

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

# 3. 🔑 Full-Screen Authentication Gate (Login Page)
if st.session_state.authenticated_key is None:
    # 🖼️ 完美还原 1600x600 高清大图的自适应视效，不拉伸不扭曲
    if os.path.exists("login_banner.png"):
        st.image("login_banner.png", use_container_width=True)
    elif os.path.exists("login_banner.jpg"):
        st.image("login_banner.jpg", use_container_width=True)
    else:
        st.title("🎨 Welcome to AI Environment Design Coach")
        st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")
        
    st.write("---")
    st.warning("👋 **Hello Student!** To unlock your AI EDC Art Director Coach, please enter your personal Gemini API Key below.")
    
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

# 4. Configure API
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]
genai.configure(api_key=st.session_state.authenticated_key)


# =====================================================================
# 🚀 THE FULL CLASSROOM PIPELINE (Stanley's Twin-Track Architecture)
# =====================================================================

# 5. Dropdown Stage Selector (Exactly at its classic intuitive position)
stage = st.selectbox(
    "📍 Choose your active pipeline design assignment stage:",
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

# 🛑 BUG FIX: Wipe history and canvas ONLY when switching stages, keeping key intact
if stage != st.session_state.previous_stage:
    st.session_state.previous_stage = stage
    st.session_state.messages = []
    if "current_image" in st.session_state:
        del st.session_state.current_image
    if "file_uploader_key" in st.session_state:
        st.session_state.file_uploader_key += 1
    else:
        st.session_state.file_uploader_key = 1
    st.rerun()

if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0


# 6. 🖼️ Sidebar: Design Canvas & The Live Summarize Dashboard Checklist
with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")
    
    needs_img = stage != "1. World Story"
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
        
    # 📋 The Live Summarize Checklist Panel
    st.subheader("📋 Design Specification")
    st.caption("This board auto-updates and turns green based on your chat answers.")
    
    active_specs = st.session_state.spec_summaries[stage]
    all_passed = True
    
    for metric, text_summary in active_specs.items():
        if text_summary and text_summary.strip().lower() != "none" and text_summary.strip() != "":
            # Turns beautiful green only when a real conceptual value exists
            st.success(f"✅ **{metric}**:\n{text_summary}")
        else:
            st.info(f"⭕ **{metric}**:\n*Pending feedback...*")
            all_passed = False
            
    st.markdown("---")
    
    # 🔄 BUG FIX 1: Classic Reset Button returned! Safely clear chat/canvas without logging out
    if st.button("🔄 Start New Critique", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.session_state.file_uploader_key += 1
        st.rerun()
        
    if st.button("🚪 Disconnect API Key", use_container_width=True):
        st.session_state.authenticated_key = None
        st.rerun()


# 7. Main Area: Header UI Setup
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

st.markdown("---")

# Render active chat threads
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 8. 🚀 THE RETURNED CLASSIC GUIDE BOX (Triggers when history is empty)
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


# 9. Chat Input Mechanics
if prompt := st.chat_input("Describe your environment concepts here..."):
    if needs_img and "current_image" not in st.session_state:
        st.warning("Please upload an image in the sidebar canvas first so the coach can review it!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()


# 10. AI Engine Model Query & Robust Block String Interception
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(
                model_name="gemini-3.1-flash-lite-preview",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            payload = [f"[PIPELINE ASSIGNMENT ZONE: {stage}]\nStudent Input: {st.session_state.messages[-1]['content']}"]
            if "current_image" in st.session_state:
                payload.append(st.session_state.current_image)
                
            response = model.generate_content(payload)
            raw_text = response.text if response.text else ""
            
            # Robust Extraction Engine: Cut through ugly markers via pure text splitting block
            display_text = raw_text
            if "[SUMMARY:" in raw_text:
                parts_split = raw_text.split("[SUMMARY:", 1)
                display_text = parts_split[0].strip()
                meta_block = parts_split[1].split("]", 1)[0].strip()
                
                # Split criteria pairs safely via pipe delimiters
                pairs = meta_block.split("|")
                for pair in pairs:
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        k_clean = k.strip()
                        v_clean = v.strip()
                        
                        # Verify dictionary and override None values smoothly
                        if k_clean in st.session_state.spec_summaries[stage]:
                            if v_clean.lower() != "none" and v_clean != "":
                                st.session_state.spec_summaries[stage][k_clean] = v_clean
                                
            st.markdown(display_text)
            st.session_state.messages.append({"role": "assistant", "content": display_text})
            st.rerun()
            
        except Exception as e:
            st.error(f"Engine Core Exception Error: {str(e)}")
