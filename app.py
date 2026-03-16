import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Environment Design Coach", page_icon="🎨", layout="centered")

# 2. Retrieve Configuration from Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
SYSTEM_INSTRUCTION = st.secrets["COMMAND_CENTER"]

# Configure Gemini API
genai.configure(api_key=API_KEY)

# 3. Header & Introduction (Requirement #1)
st.title("🎨 Environment Design Coach")
st.markdown("##### AI-Powered Studio Critique for Environment Design Students")

with st.expander("📖 How to Start & User Guide", expanded=True):
    st.write("""
    This tool simulates a **Studio Critique** with an Art Director. The coach will guide you through short, targeted questions to help clarify your design thinking.
    
    **Instructions:**
    1. Select your current **Design Phase** below.
    2. Briefly describe your concept or environment.
    3. Upload an image (Reference, Thumbnail, or Polish) if needed.
    4. The coach will prompt you with a design question.
    
    **Tip:** There are no "right" answers. You are the designer; the coach is here to help you think deeper.
    """)

# 4. Phase Selector & Reset Button (Requirement #2 & #10)
col1, col2 = st.columns([3, 1])
with col1:
    phase = st.selectbox(
        "📍 Select your design phase",
        ["Story", "Reference", "Thumbnail", "Polishing"],
        help="The coach will tailor questions based on your selected phase."
    )
with col2:
    st.write(" ") # Padding
    if st.button("🔄 Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 5. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Image Upload Section
up_file = st.file_uploader("🖼️ Upload your design (Optional)", type=["png", "jpg", "jpeg"])
if up_file:
    st.image(up_file, caption="Uploaded Design/Reference", use_container_width=True)

# 7. Example Prompts (Requirement #3)
st.markdown("""
<p style='color: #888; font-size: 0.85rem;'>
<b>Example Prompts:</b><br>
- "My environment is an abandoned train station in a cyberpunk city."<br>
- "This is a thumbnail sketch for a desert temple scene."<br>
- "This reference image inspired the lighting I want for my scene."
</p>
""", unsafe_allow_html=True)

# 8. Chat Input Logic
if prompt := st.chat_input("Describe your concept here..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 9. AI Logic & Context Injection (Requirement #5)
    try:
        # Inject the Phase into the prompt context
        context_prompt = f"[CONTEXT: Design Phase = {phase}]\nStudent Input: {prompt}"
        
        # Initialize Model (Using the preview model you confirmed)
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite-preview", 
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        with st.chat_message("assistant"):
            parts = [context_prompt]
            if up_file:
                img = Image.open(up_file)
                parts.append(img)
            
            # Generate Response
            response = model.generate_content(parts)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.error("The AI could not generate a response. Please check your instructions.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
