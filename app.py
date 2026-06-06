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
        "Primary Structure"
    ],
    "2. Exterior Reference": [
        "Terrain Type",
        "Climate & Flora",
        "Architectural Style"
    ],
    "3. Exterior Thumbnail": [
        "Narrative Composition",
        "Value & Mood",
        "Focal Point"
    ],
    "4. Interior Reference": [
        "Spatial Zone",
        "Structural Reference",
        "Style & Culture"
    ],
    "5. Interior Thumbnail": [
        "Entry & Pathways",
        "Focal Element",
        "Props Arrangement"
    ],
    "6. Exterior Polishing": [
        "Time & Lighting Mood",
        "Atmosphere & Depth",
        "Weathered Effects"
    ],
    "7. Interior Polishing": [
        "Surface Details",
        "Light Flow & Shading",
        "Usage Marks & History"
    ]
}

STAGE_DESCRIPTIONS = {
    "1. World Story": "Define the core world idea, narrative direction, and the main structure that links the exterior world to a possible interior space.",
    "2. Exterior Reference": "Select exterior references that support the world logic, terrain, climate, flora, and building language.",
    "3. Exterior Thumbnail": "Test whether the composition, value, mood, and focal point clearly communicate the story before polishing.",
    "4. Interior Reference": "Select interior references that support the spatial function, structure, and cultural logic.",
    "5. Interior Thumbnail": "Clarify circulation, focal element, prop grouping, and readable interior layout.",
    "6. Exterior Polishing": "Refine time, lighting mood, atmosphere, depth, weathering, and environmental storytelling.",
    "7. Interior Polishing": "Refine surface details, light flow, shading, and usage history."
}

OPENING_QUESTIONS = {
    "1. World Story": "Before we draw anything, think like a director: what kind of place is this, and what feeling should the audience sense when they first enter it?",
    "2. Exterior Reference": "Look at your world story first: what kind of outdoor landform would naturally shape the life, danger, or isolation of this place?",
    "3. Exterior Thumbnail": "Before adding detail, decide the viewing experience: where should the audience look first, and how should the environment guide their eye?",
    "4. Interior Reference": "Before choosing interior references, imagine the daily use of the space: what kind of activity or behaviour must this room support?",
    "5. Interior Thumbnail": "Think of the viewer walking into the room: where do they enter, and what should pull their attention deeper into the space?",
    "6. Exterior Polishing": "Before polishing, look at the ground, walls, and surrounding landscape: what material should visually dominate this exterior world?",
    "7. Interior Polishing": "Before final details, look at the surfaces closest to the viewer: what texture or material evidence should make this interior feel used and believable?"
}

STAGE_COMPLETION_MESSAGES = {
    "en": {
        "1. World Story": "Your world foundation is clear enough to continue. You may proceed to Exterior Reference if you feel ready. If you still want to develop it further, think about what kind of terrain, climate, and exterior reference would naturally support this world.",
        "2. Exterior Reference": "Your exterior reference direction is clear enough to continue. You may proceed to Exterior Thumbnail if you feel ready. If you still want to develop it further, think about which reference elements should become the main visual priority in your composition.",
        "3. Exterior Thumbnail": "Your exterior thumbnail direction is clear enough to continue. You may proceed to Interior Reference if you feel ready. If you still want to develop it further, think about whether the viewer can immediately read the story through the focal point and value structure.",
        "4. Interior Reference": "Your interior reference direction is clear enough to continue. You may proceed to Interior Thumbnail if you feel ready. If you still want to develop it further, think about how the interior structure reflects the same world logic as the exterior.",
        "5. Interior Thumbnail": "Your interior thumbnail direction is clear enough to continue. You may proceed to Exterior Polishing if you feel ready. If you still want to develop it further, think about whether the entry, focal element, and props guide the viewer clearly through the space.",
        "6. Exterior Polishing": "Your exterior polishing direction is clear enough to continue. You may proceed to Interior Polishing if you feel ready. If you still want to develop it further, think about how lighting, atmosphere, and weathering can strengthen the story.",
        "7. Interior Polishing": "Your interior polishing direction is clear enough for final refinement. If you still want to develop it further, think about whether the surface details, lighting, and usage marks clearly show how the space has been lived in."
    },
    "zh": {
        "1. World Story": "这个世界基础已经清楚，可以进入 Exterior Reference。如果你还想继续发展，可以再想想：什么样的地形、气候和室外参考最自然地支撑这个世界？",
        "2. Exterior Reference": "室外参考方向已经清楚，可以进入 Exterior Thumbnail。如果你还想继续发展，可以再想想：哪些参考元素应该成为构图里的主要视觉重点？",
        "3. Exterior Thumbnail": "室外草图方向已经清楚，可以进入 Interior Reference。如果你还想继续发展，可以再想想：观众能不能通过焦点和明暗结构马上读懂这个故事？",
        "4. Interior Reference": "室内参考方向已经清楚，可以进入 Interior Thumbnail。如果你还想继续发展，可以再想想：室内结构如何延续室外的世界逻辑？",
        "5. Interior Thumbnail": "室内草图方向已经清楚，可以进入 Exterior Polishing。如果你还想继续发展，可以再想想：入口、焦点元素和道具是否能清楚引导观众阅读空间？",
        "6. Exterior Polishing": "室外打磨方向已经清楚，可以进入 Interior Polishing。如果你还想继续发展，可以再想想：光线、氛围和风化痕迹如何进一步加强故事？",
        "7. Interior Polishing": "室内打磨方向已经清楚，可以进入最后整理。如果你还想继续发展，可以再想想：表面细节、光影和使用痕迹是否清楚说明这个空间如何被使用过？"
    }
}


# Gemini model. Keep this easy to change if Google updates model availability.
MODEL_NAME = "gemini-3.5-flash"

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
    """Gemini structured JSON schema for the active stage only.
    Uses empty strings instead of null to improve Gemini JSON reliability.
    """
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
                        "description": "Short confirmed metric value, or an empty string if not clearly confirmed."
                    }
                    for metric in metrics
                },
                "required": metrics
            },
            "rolling_summary_patch": {
                "type": "string",
                "description": "Only for Stage 1. Updated world concept summary, or an empty string for other stages."
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
        else "All metrics for this stage are already completed. Give a brief final refinement comment only. Do not force the student to move on."
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
8. The metric name is for internal checking only. Do not literally ask the student to "fill in" or "state" that metric.
9. Ask creative, reflective design questions that help the student discover the metric indirectly.
10. For extracted_metrics, only the current target metric may receive a real value. All other metrics must be an empty string "".
11. Existing locked values must not be rewritten.
12. Keep extracted metric values short: ideally 3 to 8 words.

WORLD SUMMARY RULES:
1. Only when the current stage is "1. World Story", update rolling_summary_patch.
2. The rolling_summary_patch must be a concise, coherent record of confirmed student-provided world design facts only.
3. Do not beautify by adding new facts. Do not add lore, props, weather, culture, materials, or character backstory unless the student stated them.
4. For stages 2 to 7, rolling_summary_patch must be an empty string "".

OUTPUT RULE:
Return only one complete valid JSON object. Do not use Markdown. Do not add text before or after JSON.
All values must be strings only. Never use null. Use an empty string "" when there is no value.
The JSON must follow this structure:
{{
  "ai_critique": "short student-facing critique and one question",
  "extracted_metrics": {{
    "metric name": ""
  }},
  "rolling_summary_patch": ""
}}
Keep ai_critique under 80 Chinese characters or 45 English words.
Keep rolling_summary_patch under 120 Chinese characters or 70 English words.
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



def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))

def completion_message(stage: str, student_input: str) -> str:
    lang = "zh" if contains_cjk(student_input) else "en"
    return STAGE_COMPLETION_MESSAGES[lang].get(stage, "")

def go_to_next_stage():
    current_index = st.session_state.stage_index_memory
    if current_index < len(STAGE_OPTIONS) - 1:
        st.session_state.stage_index_memory = current_index + 1
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.session_state.file_uploader_key += 1
        st.rerun()

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
    st.subheader("📍 Current Stage")
    st.info(current_selected_stage)
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
st.caption(f"Current working stage: **{stage}**")

if stage != STAGE_OPTIONS[st.session_state.stage_index_memory]:
    st.session_state.stage_index_memory = STAGE_OPTIONS.index(stage)
    st.session_state.messages = []
    if "current_image" in st.session_state:
        del st.session_state.current_image
    st.session_state.file_uploader_key += 1
    st.rerun()

# Manual story context for later-stage usage only when Stage 1 session memory is not available.
if stage != "1. World Story":
    if st.session_state.rolling_story_summary:
        st.success("✅ World Concept Summary found from Stage 1. The coach will use it for this stage.")
    else:
        st.session_state.manual_world_context = st.text_area(
            "📝 Step 1: Paste your World Concept Summary here before starting this stage:",
            value=st.session_state.manual_world_context,
            height=120,
            placeholder="Paste the Stage 1 World Concept Summary here so the coach can connect this stage to your story."
        )

st.markdown("---")

# Stage completion action button. The student controls whether to move to the next stage.
if get_active_metric(stage) is None and stage != STAGE_OPTIONS[-1]:
    st.success("✅ This stage checklist is complete. You may continue developing it here, or move to the next stage when ready.")
    if st.button(f"➡️ Move to {STAGE_OPTIONS[STAGE_OPTIONS.index(stage) + 1]}"):
        go_to_next_stage()

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
            has_world_context = bool((st.session_state.rolling_story_summary or st.session_state.manual_world_context).strip())

            if has_world_context:
                st.success("✅ **Step 1 Complete:** World Concept Summary is available.")
            else:
                st.error("⚠️ **Step 1:** Please paste your World Concept Summary above first.")

            if not has_img:
                st.error("⚠️ **Step 2:** Please upload your image in the **Sidebar Design Canvas**.")
            else:
                st.success("✅ **Step 2 Complete:** Image uploaded successfully.")

            if has_world_context and has_img:
                st.markdown("**Step 3:** Briefly explain what aspect of this design you want the coach to review.")
                st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
            else:
                st.markdown("> *The coach will begin only after the story context and image are both ready.*")
        else:
            st.markdown("**Step 1:** Briefly explain your world concept in the chat box below.")
            st.markdown(f"*Try saying: \"{example_text[stage]}\"*")
        st.markdown("---")

# =========================================================
# 10. Handle Chat Input
# =========================================================
if prompt := st.chat_input("Describe your environment concepts here..."):
    has_world_context = bool((st.session_state.rolling_story_summary or st.session_state.manual_world_context).strip())

    if stage != "1. World Story" and not has_world_context:
        st.warning("Please paste your World Concept Summary before starting this stage.")
    elif needs_img and "current_image" not in st.session_state:
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
                max_output_tokens=4096
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

            active_before_update = get_active_metric(stage)
            apply_ai_state_update(stage, ai_data)
            active_after_update = get_active_metric(stage)

            # If the student's latest answer completed the final checkpoint, append a gentle choice-based reminder.
            if active_before_update is not None and active_after_update is None:
                reminder = completion_message(stage, student_prompt)
                if reminder:
                    display_text = f"{display_text}\n\n{reminder}"

            st.markdown(display_text)
            st.session_state.messages.append({"role": "assistant", "content": display_text})
            st.rerun()

        except Exception as e:
            st.error(f"Engine Exception Error: {str(e)}")
            if "raw_text" in locals() and raw_text:
                with st.expander("DEBUG GEMINI RAW OUTPUT"):
                    st.code(raw_text)
            st.caption("If this happens repeatedly, check whether the Gemini model name is available for your API key and whether the API key has quota.")
