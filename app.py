import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import re

# 1. Page Configuration
st.set_page_config(page_title="AI Environment Design Coach", page_icon="🎨", layout="centered")

# 2. Initialize Session State (Wipe bugs and set memory arrays)
if "authenticated_key" not in st.session_state:
    st.session_state.authenticated_key = None

if "previous_stage" not in st.session_state:
    st.session_state.previous_stage = "1. World Story"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Persistent dictionary holding the real extracted summaries for each stage
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
    # BUG FIX 1: Absolutely honor Stanley's 1600x600 layout proportion without vertical stretching
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

# 4. Configure API
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]
genai.configure(api_key=st.session_state.authenticated_key)


# =====================================================================
# 🚀 TARGET ENVIRONMENT ART BIBLE ENGINE
# =====================================================================

# 5. BUG FIX 2: Layout Realignment. Put the Selector neatly inline or in an optimized grid block.
header_col, selector_col = st.columns([3, 2])

with header_col:
    st.title("AI Design Coach")
    st.markdown("##### Studio Critique System (ASMT 02 & 03)")

with selector_col:
    st.write(" ") # Padding alignment
    stage = st.selectbox(
        "🎬 Pipeline Stage:",
        [
            "1. World Story", "2. Exterior Reference", "3. Exterior Thumbnail",
            "4. Interior Reference", "5. Interior Thumbnail", "6. Exterior Polishing", "7. Interior Polishing"
        ]
    )

# 🛑 BUG FIX: Clear canvas assets and chat history smoothly when changing pipeline branches
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


# 6. 🖼️ Sidebar Workspace: Canvas Setup & Real AI Summary Dashboard
with st.sidebar:
    st.title("🖼️ Workspace Canvas")
    st.markdown("---")
    
    needs_img = stage != "1. World Story"
    if needs_img:
        up_file = st.file_uploader(
            f"Upload Graphic Asset:", 
            type=["png", "jpg", "jpeg"],
            key=f"uploader_{st.session_state.file_uploader_key}"
        )
        if up_file:
            st.session_state.current_image = Image.open(up_file)
        
        if "current_image" in st.session_state and st.session_state.current_image is not None:
            st.image(st.session_state.current_image, caption="Active Artwork Review", use_container_width=True)
            if st.button("🗑️ Clear Canvas Asset", use_container_width=True):
                del st.session_state.current_image
                st.session_state.file_uploader_key += 1
                st.rerun()
        st.markdown("---")
        
    # 🟢 Real Intelligence Tracking Board (No more blind automatic counts!)
    st.subheader("📋 Design Specification")
    st.caption("Summarized details extracted live from studio discourse.")
    
    active_specs = st.session_state.spec_summaries[stage]
    stage_complete = True
    
    for metric, text_value in active_specs.items():
        if text_value and text_value.strip() != "":
            # Turn beautifully green only when the AI extracts real architectural context
            st.success(f"✅ **{metric}**:\n{text_value}")
        else:
            st.info(f"⭕ **{metric}**:\n*Pending feedback...*")
            stage_complete = False
            
    if stage_complete:
        st.markdown("---")
        st.balloons()
        st.success("🌟 **[STAGE READY]** Core specs met! Switch selector above to progress the pipeline.")


# 7. Guidelines Dashboard Container
with st.expander("📖 Guide: Assignment Milestones", expanded=False):
    st.markdown("""
    * **Workflow**: Fill the description or canvas inside the sidebar, talk to the Coach, and watch your specification summary build up on the left side menu!
    """)

# Render historical messages cleanly without parsing system hashes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Prompt reminders for empty message arrays
if len(st.session_state.messages) == 0:
    has_img = "current_image" in st.session_state
    example_prompts = {
        "1. World Story": "My concept is an old abandoned train station inside a swamp forest.",
        "2. Exterior Reference": "I've uploaded reference boards for decayed wood architecture textures.",
        "3. Exterior Thumbnail": "Uploading my silhouette composition sketch to evaluate depth separation.",
        "4. Interior Reference": "Sourcing references for a tight industrial bunker command layout room.",
        "5. Interior Thumbnail": "This layout blueprint sets the entryways and coordinates the core desk prop.",
        "6. Exterior Polishing": "Currently blending moss textures over stone steps under heavy ambient fog.",
        "7. Interior Polishing": "Refining wood speculative values matching single window directional moon rays."
    }
    
    if needs_img and not has_img:
        st.error("⚠️ **Asset Missing**: Upload matching artwork inside the **Sidebar Workspace Canvas** first to start review.")
    else:
        st.info(f"💡 **Suggested Prompt for {stage[3:]}:** \"{example_prompts[stage]}\"")

# 8. Processing Chat Stream Interception & Dynamic Data Extraction
if prompt := st.chat_input("Input design intent..."):
    if needs_img and "current_image" not in st.session_state:
        st.error("Upload graphical file first!")
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
            
            # Pack current pipeline phase as high-priority guidance metadata
            formatted_prompt = f"[STUDIO SYSTEM PHASE: {stage}]\nStudent Input: {st.session_state.messages[-1]['content']}"
            payload = [formatted_prompt]
            if "current_image" in st.session_state:
                payload.append(st.session_state.current_image)
                
            response = model.generate_content(payload)
            raw_text = response.text if response.text else ""
            
            # 🔍 Data Extractor: Check if the raw text contains the structural summary syntax array
            # Expected format from secrets instruction: [SUMMARY: Metric1=Text|Metric2=Text|Metric3=Text]
            cleaned_text = raw_text
            match = re.search(r"\[SUMMARY:\s*(.*?)\]", raw_text, re.DOTALL)
            
            if match:
                summary_block = match.group(1)
                # Cut the hidden token cleanly out so the student never sees the ugly raw tag strings
                cleaned_text = raw_text.replace(match.group(0), "").strip()
                
                # Split entries via delimiter safely
                pairs = summary_block.split("|")
                for pair in pairs:
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        k_clean = k.strip()
                        v_clean = v.strip()
                        # Update the specific parameter tracking index seamlessly if valid
                        if k_clean in st.session_state.spec_summaries[stage] and v_clean.lower() != "none" and v_clean != "":
                            st.session_state.spec_summaries[stage][k_clean] = v_clean
            
            st.markdown(cleaned_text)
            st.session_state.messages.append({"role": "assistant", "content": cleaned_text})
            st.rerun()
            
        except Exception as e:
            st.error(f"Engine Core Fault: {str(e)}")
