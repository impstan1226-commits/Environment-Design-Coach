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
    "1. World Story": "Define the story foundation: world feeling, narrative situation, and the main exterior structure that can lead into the interior.",
    "2. Exterior Reference": "Select exterior references that support the terrain, climate, vegetation, and architectural language of the world.",
    "3. Exterior Thumbnail": "Test whether the composition, value arrangement, and focal point can clearly express the story before polishing.",
    "4. Interior Reference": "Select interior references that support the spatial function, structure, culture, and lived logic.",
    "5. Interior Thumbnail": "Clarify circulation, focal element, prop grouping, and readable interior layout.",
    "6. Exterior Polishing": "Refine exterior time, lighting mood, atmosphere, depth, and weathering effects.",
    "7. Interior Polishing": "Refine interior surfaces, light flow, shading, usage marks, and history."
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

UPLOAD_REQUIREMENTS = {
    "2. Exterior Reference": "Upload your exterior reference moodboard.",
    "3. Exterior Thumbnail": "Upload your exterior thumbnail sheet with A, B, C options.",
    "4. Interior Reference": "Upload your interior reference moodboard.",
    "5. Interior Thumbnail": "Upload your interior top view and thumbnail sheet with A, B, C options.",
    "6. Exterior Polishing": "Upload your exterior final artwork or polishing progress.",
    "7. Interior Polishing": "Upload your interior final artwork or polishing progress."
}


METRIC_GUIDANCE = {
    "Theme & Type": {
        "accept_when": "The student has made the world direction clear through natural story description, setting, or visual direction. Accept simple descriptions such as a lonely blacksmith in a realistic forest, a magic house, a ruined city, a cave village, or an abandoned station.",
        "question_style": "Do not ask for genre, mood, atmosphere, or theme words directly. If the student is only greeting, simply ask them to tell you the rough story in plain words: who or what the place is for, where it is, and what is happening there."
    },
    "World Narrative": {
        "accept_when": "The student has explained what is happening in this world, who uses or inhabits the space, or what situation gives the environment meaning.",
        "question_style": "Ask about the situation, daily life, conflict, purpose, or relationship between the character and the place."
    },
    "Primary Structure": {
        "accept_when": "The student has identified a main exterior structure that can logically connect to an interior, such as a house, cabin, cave entrance, dungeon entrance, workshop, tower, gate, bunker, temple, or ruins.",
        "question_style": "Ask what visible structure in the exterior will become the entry point or source for the later interior design."
    },
    "Terrain Type": {
        "accept_when": "The student has clearly chosen the exterior landform or ground condition, such as mountain, swamp, desert, forest clearing, canyon, coastline, city ruin, cave mouth, or valley.",
        "question_style": "Ask what landform would naturally support the world story and affect how characters move or survive."
    },
    "Climate & Flora": {
        "accept_when": "The student has identified climate, season, vegetation, or plant reference direction that supports the environment.",
        "question_style": "Ask how climate and plant life reveal the world’s condition rather than asking for random plant names."
    },
    "Architectural Style": {
        "accept_when": "The student has described the exterior building language, construction influence, or style logic, such as wooden rural, stone medieval, industrial, nomadic, bunker-like, temple-based, or makeshift.",
        "question_style": "Ask what construction language makes the structure belong to this world."
    },
    "Narrative Composition": {
        "accept_when": "The student has chosen or discussed a thumbnail arrangement and explained a visual intention, such as foreground framing, hiding/revealing the house, scale contrast, discovery, protection, isolation, journey, or where the story should be read in the layout.",
        "question_style": "Ask whether the arrangement of shapes, scale, and placement helps the viewer understand the story before reading any explanation."
    },
    "Value & Mood": {
        "accept_when": "The student has identified value contrast, light-dark grouping, or mood direction in the thumbnail.",
        "question_style": "Ask how light and dark areas support the emotional reading of the scene."
    },
    "Focal Point": {
        "accept_when": "The student has stated the main visual focus, such as the house, entrance, book, tree, character, prop, or light target, or clearly says what the viewer should look at first.",
        "question_style": "Ask what the audience should notice first and why it matters to the story."
    },
    "Spatial Zone": {
        "accept_when": "The student has defined the interior type or zone, such as bedroom, workshop, cave chamber, hall, shrine, kitchen, control room, or storage area.",
        "question_style": "Ask what activity this interior must support."
    },
    "Structural Reference": {
        "accept_when": "The student has identified interior construction reference, such as beams, arches, cave walls, columns, ceiling type, supports, stairs, platforms, or wall structure.",
        "question_style": "Ask what structural evidence makes the room feel believable."
    },
    "Style & Culture": {
        "accept_when": "The student has linked interior design to cultural, historical, lifestyle, or world-specific visual logic.",
        "question_style": "Ask what cultural or lifestyle clues should appear in the space."
    },
    "Entry & Pathways": {
        "accept_when": "The student has clarified entrance, movement path, or circulation through the interior thumbnail.",
        "question_style": "Ask how the viewer or character enters and moves through the room."
    },
    "Focal Element": {
        "accept_when": "The student has chosen the central object, zone, or feature that anchors the interior, such as forge, bed, altar, table, machine, throne, fireplace, or workbench.",
        "question_style": "Ask what object or area tells the audience the purpose of the room first."
    },
    "Props Arrangement": {
        "accept_when": "The student has described how props are grouped, placed, or arranged to support function and story.",
        "question_style": "Ask how props show daily use, habit, status, or history."
    },
    "Time & Lighting Mood": {
        "accept_when": "The student has selected time of day and lighting mood for the exterior polish.",
        "question_style": "Ask what time and light condition best supports the story mood."
    },
    "Atmosphere & Depth": {
        "accept_when": "The student has described atmospheric depth such as mist, dust, haze, rain, snow, smoke, heat, distance fade, or clear layered air.",
        "question_style": "Ask how atmosphere separates foreground, midground, and background."
    },
    "Weathered Effects": {
        "accept_when": "The student has described exterior wear, age, damage, dirt, moss, rust, cracks, erosion, water stains, or environmental impact.",
        "question_style": "Ask what marks prove the exterior has existed over time."
    },
    "Surface Details": {
        "accept_when": "The student has described interior texture or material surface details such as wood grain, stone roughness, fabric, metal, dust, scratches, or handmade marks.",
        "question_style": "Ask what close-up surface evidence makes the interior believable."
    },
    "Light Flow & Shading": {
        "accept_when": "The student has explained how light enters, travels, casts shadows, or creates contrast in the interior.",
        "question_style": "Ask how the light moves through the room and what it hides or reveals."
    },
    "Usage Marks & History": {
        "accept_when": "The student has described signs of use, age, repair, routine, damage, storage, mess, or personal history inside the space.",
        "question_style": "Ask what marks show that people have actually lived or worked there."
    }
}

STAGE_COMPLETION_PROMPTS = {
    "1. World Story": "If you still want to develop this idea, you can think about what kind of terrain would naturally support this world and the main structure.",
    "2. Exterior Reference": "If you still want to develop this stage, you can compare whether the terrain, climate, and architecture references are speaking the same visual language.",
    "3. Exterior Thumbnail": "If you still want to develop this stage, you can test whether the story is readable before adding details.",
    "4. Interior Reference": "If you still want to develop this stage, you can think about whether the interior references clearly support the activity, structure, and culture of the space.",
    "5. Interior Thumbnail": "If you still want to develop this stage, you can check whether the viewer understands the entrance, focal element, and prop logic without explanation.",
    "6. Exterior Polishing": "If you still want to develop this stage, you can refine how time, atmosphere, and weathering strengthen the story mood.",
    "7. Interior Polishing": "If you still want to develop this stage, you can refine how surfaces, light, and usage marks reveal the history of the interior."
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

if "stage_ready_notice" not in st.session_state:
    st.session_state.stage_ready_notice = False

if "stage_ready_language" not in st.session_state:
    st.session_state.stage_ready_language = "en"

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

def detect_language_from_text(text):
    """Simple language detector for stage-completion messages."""
    if not text:
        return "en"
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    return "en"

def get_stage_ready_message(stage, next_stage=None, lang="en"):
    """Message shown below the latest AI reply when all checkpoints in a stage are complete."""
    if lang == "zh":
        if next_stage:
            return f"目前这个阶段的信息已经足够进入下一阶段。你可以选择继续发展这个阶段，或进入 **{next_stage}**。"
        return "目前最后阶段的信息已经足够完整。你可以继续微调细节，或把这些记录用于最终 Art Bible presentation。"
    if next_stage:
        return f"This stage is clear enough to continue. You may keep developing this stage, or move to **{next_stage}**."
    return "This final stage is clear enough. You may continue refining details, or use these notes for your final Art Bible presentation."

def get_continue_development_prompt(stage, lang="en"):
    """Follow-up prompt generated only when the student chooses to continue developing."""
    zh_prompts = {
        "1. World Story": "如果你想继续发展，可以进一步思考：这个世界的地形如何支撑角色的生活方式和主要建筑？",
        "2. Exterior Reference": "如果你想继续发展，可以比较：地形、气候植物和建筑参考是否属于同一种视觉语言？",
        "3. Exterior Thumbnail": "如果你想继续发展，可以检查：在还没加细节之前，观众能不能从构图中看懂故事？",
        "4. Interior Reference": "如果你想继续发展，可以思考：这些室内参考是否清楚支持空间活动、结构和文化背景？",
        "5. Interior Thumbnail": "如果你想继续发展，可以检查：观众是否能不靠解释就看懂入口、焦点元素和道具逻辑？",
        "6. Exterior Polishing": "如果你想继续发展，可以进一步强化：时间、空气层次和老化痕迹如何让故事更可信？",
        "7. Interior Polishing": "如果你想继续发展，可以继续推敲：表面、光影和使用痕迹如何说明这个空间的历史？"
    }
    en_prompts = {
        "1. World Story": "If you still want to develop this idea, think about what kind of terrain would naturally support the character’s life and the main structure.",
        "2. Exterior Reference": "If you still want to develop this stage, compare whether the terrain, climate, flora, and architecture references speak the same visual language.",
        "3. Exterior Thumbnail": "If you still want to develop this stage, test whether the story is readable from the composition before adding details.",
        "4. Interior Reference": "If you still want to develop this stage, check whether the interior references clearly support the activity, structure, and culture of the space.",
        "5. Interior Thumbnail": "If you still want to develop this stage, check whether the viewer can understand the entrance, focal element, and prop logic without explanation.",
        "6. Exterior Polishing": "If you still want to develop this stage, refine how time, atmosphere, and weathering make the story more believable.",
        "7. Interior Polishing": "If you still want to develop this stage, refine how surfaces, light, and usage marks reveal the history of the interior."
    }
    return (zh_prompts if lang == "zh" else en_prompts).get(stage, "")

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
        f"The current target checkpoint is: {active_metric}. "
        f"Acceptance guide: {METRIC_GUIDANCE.get(active_metric, {}).get('accept_when', '')} "
        f"Question style: {METRIC_GUIDANCE.get(active_metric, {}).get('question_style', '')}"
        if active_metric
        else "All checkpoints for this stage are already completed. Give a brief final refinement comment only."
    )

    recent_context = []
    for m in st.session_state.messages[-8:]:
        role = "Student" if m.get("role") == "user" else "Coach"
        recent_context.append(f"{role}: {m.get('content', '')}")
    recent_context_text = "\n".join(recent_context)

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

RECENT CONVERSATION CONTEXT:
{recent_context_text if recent_context_text else "No prior conversation in this stage."}

STUDENT'S LATEST INPUT:
{student_input}

IMAGE STATUS:
{"An image has been uploaded and is available for visual critique." if has_image else "No image is available in this turn."}

STRICT BEHAVIOUR RULES:
1. {language_rule}
2. The visible critique must be short: 1 to 3 sentences only.
3. Behave like a studio director training the student to think, not like a form asking for checklist answers.
4. Do not ask direct checklist questions such as "what is your theme and type?" or "state your architectural identity".
5. Do not invent story, architecture, terrain, culture, props, materials, lighting, or emotional meaning that the student has not stated or shown.
6. Follow the turn protocol strictly. {active_metric_rule}
7. If the current target checkpoint is not yet clearly answered, ask exactly ONE focused, story-led design question about that checkpoint.
8. The conversation should generally move through checkpoints in order, but do not ignore clear student decisions that answer a later checkpoint.
9. Extract checkpoint values when the student has clearly provided concrete design decisions in the latest input, recent conversation, confirmed summary, or uploaded image discussion.
10. The checkpoint name is for internal checking only. Do not literally ask the student to "fill in" or "state" that checkpoint.
11. Ask creative, reflective design questions that help the student discover the checkpoint indirectly.
12. For extracted_metrics, you may fill any clearly answered checkpoint for the current stage, but do not fill vague, guessed, or unrelated values. Leave unanswered checkpoints as empty strings "".
13. Existing locked values must not be rewritten.
14. If the student only greets you or says something unrelated, do not extract any checkpoint and do not mention professional terms such as theme, genre, mood, atmosphere, composition, value, or focal point. Reply naturally in plain language and invite the student to describe the idea as a simple story: who or what is there, where it is, and what is happening.
15. Keep extracted checkpoint values short: ideally 3 to 8 words.

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
    """Update dashboard and summary without allowing overwrites.
    V8 allows non-linear checkpoint locking when the student clearly answers a later point.
    """
    extracted = ai_data.get("extracted_metrics", {})

    if isinstance(extracted, dict):
        for metric in STAGE_METRICS[stage]:
            candidate = extracted.get(metric)
            current_value = st.session_state.spec_summaries[stage].get(metric)

            # Lock once only. Never overwrite a green value.
            if current_value is None and is_meaningful_value(candidate):
                st.session_state.spec_summaries[stage][metric] = shorten_metric_value(candidate)

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
    st.subheader("📍 Current Stage")
    st.info(current_selected_stage)
    st.markdown("---")

    if needs_img:
        upload_instruction = UPLOAD_REQUIREMENTS.get(current_selected_stage, "Upload your design image for this stage.")
        up_file = st.file_uploader(
            upload_instruction,
            type=["png", "jpg", "jpeg"],
            key=f"uploader_{st.session_state.file_uploader_key}"
        )
        st.caption(f"Required upload: {upload_instruction}")

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
        st.session_state.stage_ready_language = "en"
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
    3. Upload the required **stage image** when needed (moodboard, thumbnail sheet, top view, or polishing progress).
    """)

stage = st.selectbox(
    "🔑 Choose your active pipeline design assignment stage:",
    STAGE_OPTIONS,
    index=st.session_state.stage_index_memory
)

if stage != STAGE_OPTIONS[st.session_state.stage_index_memory]:
    st.session_state.stage_index_memory = STAGE_OPTIONS.index(stage)
    st.session_state.messages = []
    st.session_state.stage_ready_notice = False
    st.session_state.stage_ready_language = "en"
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

# Render chat history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Stage completion action appears directly below the latest AI reply.
if st.session_state.stage_ready_notice:
    current_index = STAGE_OPTIONS.index(stage)
    next_stage = STAGE_OPTIONS[current_index + 1] if current_index < len(STAGE_OPTIONS) - 1 else None
    lang = st.session_state.get("stage_ready_language", "en")

    with st.chat_message("assistant"):
        st.success(get_stage_ready_message(stage, next_stage, lang))
        col_next, col_keep = st.columns(2)

        with col_next:
            if next_stage and st.button(f"➡️ Move to {next_stage}", use_container_width=True, key=f"move_next_{stage}"):
                st.session_state.stage_index_memory = STAGE_OPTIONS.index(next_stage)
                st.session_state.messages = []
                st.session_state.stage_ready_notice = False
                if "current_image" in st.session_state:
                    del st.session_state.current_image
                st.session_state.file_uploader_key += 1
                st.rerun()

        with col_keep:
            if st.button("💬 Continue developing this stage", use_container_width=True, key=f"continue_{stage}"):
                follow_up = get_continue_development_prompt(stage, lang)
                if follow_up:
                    st.session_state.messages.append({"role": "assistant", "content": follow_up})
                st.session_state.stage_ready_notice = False
                st.rerun()

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
                st.error(f"⚠️ **Step 2:** {UPLOAD_REQUIREMENTS.get(stage, 'Please upload your image in the Sidebar Design Canvas.')}")
            else:
                st.success(f"✅ **Step 2 Complete:** {UPLOAD_REQUIREMENTS.get(stage, 'Image uploaded successfully.')}")

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
        st.session_state.stage_ready_notice = False
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

            apply_ai_state_update(stage, ai_data)

            stage_is_complete = all(
                is_meaningful_value(st.session_state.spec_summaries[stage].get(metric))
                for metric in STAGE_METRICS[stage]
            )
            if stage_is_complete:
                st.session_state.stage_ready_notice = True
                st.session_state.stage_ready_language = detect_language_from_text(student_prompt)

            st.markdown(display_text)
            st.session_state.messages.append({"role": "assistant", "content": display_text})
            st.rerun()

        except Exception as e:
            st.error(f"Engine Exception Error: {str(e)}")
            if "raw_text" in locals() and raw_text:
                with st.expander("DEBUG GEMINI RAW OUTPUT"):
                    st.code(raw_text)
            st.caption("If this happens repeatedly, check whether the Gemini model name is available for your API key and whether the API key has quota.")
