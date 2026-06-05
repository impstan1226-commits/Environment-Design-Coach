import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import re

# =========================================================
# 1. Page Configuration
# =========================================================
st.set_page_config(
    page_title="AI Environment Design Coach",
    page_icon="🎨",
    layout="centered"
)

# =========================================================
# 2. Fixed Teaching Pipeline Data
# =========================================================
STAGE_OPTIONS = [
    "1. World Story",
    "2. Exterior Reference",
    "3. Exterior Thumbnail",
    "4. Interior Reference",
    "5. Interior Thumbnail",
    "6. Exterior Polishing",
    "7. Interior Polishing"
]

STAGE_METRICS = {
    "1. World Story": [
        "Theme & Type",
        "World Narrative",
        "Architectural Identity"
    ],
    "2. Exterior Reference": [
        "Terrain Type",
        "Flora Reference",
        "Architectural Style"
    ],
    "3. Exterior Thumbnail": [
        "Composition Guide",
        "Value in Environment",
        "Horizon & Eye-Level"
    ],
    "4. Interior Reference": [
        "Spatial Zone",
        "Structural Reference",
        "Style & Culture"
    ],
    "5. Interior Thumbnail": [
        "Entry & Pathways",
        "Focal Hero Furniture",
        "Props Arrangement"
    ],
    "6. Exterior Polishing": [
        "Landscape Material",
        "Lighting & Atmosphere",
        "Weathered Effects"
    ],
    "7. Interior Polishing": [
        "Texture/Material Detail",
        "Light Flow & Contrast",
        "Usage Marks & History"
    ]
}

STAGE_DESCRIPTIONS = {
    "1. World Story": "Define the core world idea before any visual design decision.",
    "2. Exterior Reference": "Select exterior references that support the world logic, terrain, vegetation, and building language.",
    "3. Exterior Thumbnail": "Clarify composition, value hierarchy, depth, horizon, and eye-level before polishing.",
    "4. Interior Reference": "Select interior references that support the spatial function, structure, and cultural logic.",
    "5. Interior Thumbnail": "Clarify circulation, focal furniture, prop grouping, and readable interior layout.",
    "6. Exterior Polishing": "Refine exterior material, atmosphere, lighting, weathering, and environmental storytelling.",
    "7. Interior Polishing": "Refine interior textures, artificial/natural light flow, contrast, and usage history."
}

OPENING_QUESTIONS = {
    "1. World Story": "Before we design anything, define the foundation clearly: what is the main theme and environment type of your world?",
    "2. Exterior Reference": "Start by connecting your exterior reference to the story. What terrain type best supports this world?",
    "3. Exterior Thumbnail": "Focus on structure before detail. What composition guide are you using to control the viewer's eye?",
    "4. Interior Reference": "Before choosing interior references, define the function. What spatial zone are you designing?",
    "5. Interior Thumbnail": "Start with movement. Where does the viewer enter, and how should the pathway guide the eye?",
    "6. Exterior Polishing": "Before adding effects, define the surface logic. What is the dominant landscape material?",
    "7. Interior Polishing": "Before final details, define the material logic. What texture or material detail must be clearly visible?"
}

# Gemini model. Keep this easy to change if Google updates model availability.
MODEL_NAME = "gemini-1.5-flash-latest"

# =========================================================
# 3. Session State
# =========================================================
def fresh_spec_summaries():
    return {
        stage: {metric: None for metric in metrics}
        for stage, metrics in STAGE_METRICS.items()
    }

if "authenticated_key" not in st.session_state:
    st.session_state.authenticated_key = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "spec_summaries" not in st.session_state:
    st.session_state.spec_summaries = fresh_spec_summaries()

if "rolling_story_summary" not in st.session_state:
    st.session_state.rolling_story_summary = ""

if "manual_world_context" not in st.session_state:
    st.session_state.manual_world_context = ""

if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

if "stage_index_memory" not in st.session_state:
    st.session_state.stage_index_memory = 0

# =========================================================
# 4. Helper Functions
# =========================================================
def get_active_metric(stage: str):
    """Return the first incomplete metric for the current stage."""
    for metric in STAGE_METRICS[stage]:
        value = st.session_state.spec_summaries[stage].get(metric)
        if not value:
            return metric
    return None

def is_meaningful_value(value):
    """Reject empty, fake, or null-like values."""
    if value is None:
        return False
    if not isinstance(value, str):
        return False
    cleaned = value.strip()
    if cleaned == "":
        return False
    if cleaned.lower() in ["none", "null", "n/a", "not mentioned", "pending", "unknown"]:
        return False
    return True

def shorten_metric_value(value, max_words=8):
    """Keep dashboard values short and readable."""
    value = re.sub(r"\s+", " ", value.strip())
    words = value.split(" ")
    if len(words) > max_words:
        return " ".join(words[:max_words])
    return value

def extract_json_object(raw_text):
    """Robustly parse Gemini JSON, including accidental Markdown fences."""
    if not raw_text:
        raise ValueError("Empty AI response.")

    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise

def build_response_schema(stage: str):
    """Gemini structured JSON schema for the active stage only."""
    metrics = STAGE_METRICS[stage]
    return {
        "type": "object",
        "properties": {
            "ai_critique": {
                "type": "string",
                "description": "The short critique shown to the student."
            },
            "extracted_metrics": {
                "type": "object",
                "properties": {
                    metric: {
                        "type": "string",
                        "description": "Short confirmed metric value, or null if not clearly confirmed."
                    }
                    for metric in metrics
                },
                "required": metrics
            },
            "rolling_summary_patch": {
                "type": "string",
                "description": "Only for Stage 1. Updated world concept summary, or null/empty for other stages."
            }
        },
        "required": [
            "ai_critique",
            "extracted_metrics",
            "rolling_summary_patch"
        ]
    }

def build_ai_instruction(stage: str, student_input: str, has_image: bool):
    """Build a compact but strict instruction for Gemini on each turn."""
    active_metric = get_active_metric(stage)
    completed_specs = st.session_state.spec_summaries[stage]
    world_context = st.session_state.rolling_story_summary or st.session_state.manual_world_context

    language_rule = (
        "Reply in the same language used by the student. "
        "If the student mixes languages, reply in the dominant language."
    )

    active_metric_rule = (
        f"The current target metric is: {active_metric}."
        if active_metric
        else "All metrics for this stage are already completed. Give a brief final refinement comment only."
    )

    locked_specs_text = json.dumps(completed_specs, ensure_ascii=False, indent=2)

    instruction = f"""
You are AI EDC, a strict but helpful Environment Art Director for concept art students.

CURRENT STAGE:
{stage}

STAGE PURPOSE:
{STAGE_DESCRIPTIONS[stage]}

VALID METRICS FOR THIS STAGE:
{STAGE_METRICS[stage]}

ALREADY LOCKED DESIGN SPECIFICATION VALUES:
{locked_specs_text}

WORLD CONCEPT CONTEXT:
{world_context if world_context else "No world concept context has been provided yet."}

STUDENT'S LATEST INPUT:
{student_input}

IMAGE STATUS:
{"An image has been uploaded and is available for visual critique." if has_image else "No image is available in this turn."}

STRICT BEHAVIOUR RULES:
1. {language_rule}
2. The visible critique must be short: 1 to 3 sentences only.
3. Do not invent story, architecture, terrain, culture, props, materials, lighting, or emotional meaning that the student has not stated or shown.
4. Follow the turn protocol strictly. {active_metric_rule}
5. If the current target metric is not yet clearly answered, ask exactly ONE focused question about that metric.
6. Do not ask about later metrics until the current target metric is accepted.
7. Only extract a metric value when the student has clearly provided a concrete design decision.
8. For extracted_metrics, only the current target metric may receive a real value. All other metrics must be null.
9. Existing locked values must not be rewritten.
10. Keep extracted metric values short: ideally 3 to 8 words.

WORLD SUMMARY RULES:
1. Only when the current stage is "1. World Story", update rolling_summary_patch.
2. The rolling_summary_patch must be a concise, coherent record of confirmed student-provided world design facts only.
3. Do not beautify by adding new facts. Do not add lore, props, weather, culture, materials, or character backstory unless the student stated them.
4. For stages 2 to 7, rolling_summary_patch must be null.

OUTPUT RULE:
Return only a valid JSON object with this exact structure:
{{
  "ai_critique": "...",
  "extracted_metrics": {{
    "metric name": null or "short confirmed value"
  }},
  "rolling_summary_patch": null or "updated summary"
}}
"""
    return instruction.strip()

def apply_ai_state_update(stage: str, ai_data: dict):
    """Update dashboard and summary without allowing overwrites or hallucinated mass updates."""
    active_metric = get_active_metric(stage)
    extracted = ai_data.get("extracted_metrics", {})

    if active_metric and isinstance(extracted, dict):
        candidate = extracted.get(active_metric)
        current_value = st.session_state.spec_summaries[stage].get(active_metric)

        # Lock once only. Never overwrite a green value.
        if current_value is None and is_meaningful_value(candidate):
            st.session_state.spec_summaries[stage][active_metric] = shorten_metric_value(candidate)

    if stage == "1. World Story":
        summary_patch = ai_data.get("rolling_summary_patch")
        if is_meaningful_value(summary_patch):
            st.session_state.rolling_story_summary = summary_patch.strip()

# =========================================================
# 5. Full-Screen Authentication Gate
# =========================================================
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

# =========================================================
# 6. Configure Gemini
# =========================================================
genai.configure(api_key=st.session_state.authenticated_key)

# Optional short secret. Do not place long stage rules in Secrets anymore.
BASE_SECRET_INSTRUCTION = st.secrets.get(
    "COMMAND_CENTER",
    "You are AI EDC, an Environment Art Director for concept art students."
)

# =========================================================
# 7. Sidebar Panel
# =========================================================
current_selected_stage = STAGE_OPTIONS[st.session_state.stage_index_memory]
needs_img = current_selected_stage != "1. World Story"

with st.sidebar:
    st.title("🖼️ Design Canvas")
    st.markdown("---")

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
            st.image(
                st.session_state.current_image,
                caption="Current Review Object",
                use_container_width=True
            )
            if st.button("🗑️ Remove Image", use_container_width=True):
                del st.session_state.current_image
                st.session_state.file_uploader_key += 1
                st.rerun()
        st.markdown("---")

    st.subheader("📋 Design Specification")
    st.caption("This board auto-updates and unlocks green marks when the AI approves your inputs.")

    active_specs = st.session_state.spec_summaries[current_selected_stage]

    for metric, text_summary in active_specs.items():
        if text_summary and str(text_summary).strip().lower() not in ["none", "null", ""]:
            st.success(f"✅ **{metric}**:\n{text_summary}")
        else:
            st.info(f"⭕ **{metric}**:\n*Pending feedback...*")

    if current_selected_stage == "1. World Story":
        st.markdown("---")
        st.subheader("📝 World Concept Summary")
        if st.session_state.rolling_story_summary:
            st.info(st.session_state.rolling_story_summary)
        else:
            st.caption("*The Art Director will continuously compile your confirmed world concept here.*")

    st.markdown("---")

    if st.button("🔄 Start New Critique", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.session_state.file_uploader_key += 1
        st.session_state.stage_index_memory = 0
        st.session_state.rolling_story_summary = ""
        st.session_state.manual_world_context = ""
        st.session_state.spec_summaries = fresh_spec_summaries()
        st.rerun()

    if st.button("🚪 Disconnect API Key", use_container_width=True):
        st.session_state.authenticated_key = None
        st.rerun()

# =========================================================
# 8. Main Area Content Rendering
# =========================================================
st.title("AI Environment Design Coach")
st.markdown("#### An AI-Guided Studio Critique System for Concept Art Education")
st.info("**AI EDC Hint:** Talk with the studio Art Director to refine your Environment Art Bible requirements.")

with st.expander("📖 How to Start & User Guide", expanded=False):
    st.write("**This tool simulates a studio critique with an art director to guide environment design thinking.**")
    st.markdown("""
    1. Choose your **design stage**.
    2. Briefly describe your **idea** in the chat.
    3. Upload an **image** if needed (for Reference, Thumbnail, and Polishing stages).
    """)

stage = st.selectbox(
    "🔑 Choose your active pipeline design assignment stage:",
    STAGE_OPTIONS,
    index=st.session_state.stage_index_memory
)

if stage != STAGE_OPTIONS[st.session_state.stage_index_memory]:
    st.session_state.stage_index_memory = STAGE_OPTIONS.index(stage)
    st.session_state.messages = []
    if "current_image" in st.session_state:
        del st.session_state.current_image
    st.session_state.file_uploader_key += 1
    st.rerun()

# Manual story context for later-stage usage when session memory is lost.
if stage != "1. World Story":
    default_context = st.session_state.rolling_story_summary or st.session_state.manual_world_context
    st.session_state.manual_world_context = st.text_area(
        "📝 Paste your World Concept Summary here before starting this stage:",
        value=default_context,
        height=120,
        placeholder="Paste the Stage 1 World Concept Summary here so the coach can connect this stage to your story."
    )

st.markdown("---")

# Opening prompt when no chat exists.
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown(OPENING_QUESTIONS[stage])

# Render chat history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================================================
# 9. Guide Boxes
# =========================================================
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
                st.markdown("**Step 2:** Briefly explain your design intent in the chat box below.")
                st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
        else:
            st.markdown("**Step 1:** Briefly explain your world concept in the chat box below.")
            st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
        st.markdown("---")

# =========================================================
# 10. Handle Chat Input
# =========================================================
if prompt := st.chat_input("Describe your environment concepts here..."):
    if needs_img and "current_image" not in st.session_state:
        st.warning("Please upload an image in the sidebar canvas first so the coach can review it!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# =========================================================
# 11. Core Gemini JSON Query Engine
# =========================================================
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            student_prompt = st.session_state.messages[-1]["content"]
            has_image = "current_image" in st.session_state and st.session_state.current_image is not None

            ai_instruction = build_ai_instruction(
                stage=stage,
                student_input=student_prompt,
                has_image=has_image
            )

            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                system_instruction=BASE_SECRET_INSTRUCTION
            )

            payload = [ai_instruction]
            if has_image:
                payload.append(st.session_state.current_image)

            generation_config = genai.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=build_response_schema(stage),
                max_output_tokens=1024
            )

            response = model.generate_content(
                payload,
                generation_config=generation_config
            )

            raw_text = response.text if response and response.text else ""
            ai_data = extract_json_object(raw_text)

            display_text = ai_data.get("ai_critique", "").strip()
            if not display_text:
                display_text = "I need a clearer design decision before I can update the board. Please clarify the current design point."

            apply_ai_state_update(stage, ai_data)

            st.markdown(display_text)
            st.session_state.messages.append({"role": "assistant", "content": display_text})
            st.rerun()

        except Exception as e:
            st.error(f"Engine Exception Error: {str(e)}")
            st.caption("If this happens repeatedly, check whether the Gemini model name is available for your API key and whether the API key has quota.")
