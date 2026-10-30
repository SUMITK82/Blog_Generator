import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# ==========================================
# 1. PAGE CONFIG & ADVANCED CSS
# ==========================================
st.set_page_config(page_title="WriteFlow AI", page_icon="🪶", layout="centered")

st.markdown("""
    <style>
    /* Main Container Padding */
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 900px; }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161625;
        border-right: 1px solid #2d2d3d;
    }

    /* Auto-expanding Text Area */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #3b3b4f;
        background-color: #1e1e2e;
        color: #fff;
        font-size: 15px;
        padding: 12px;
        resize: vertical !important;
        transition: border-color 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #4F46E5;
        box-shadow: 0 0 0 1px #4F46E5;
    }

    /* Primary Gradient Button */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 48px;
        font-weight: 600;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
        color: white;
    }

    /* Header Branding */
    .header-box {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding-bottom: 20px;
        border-bottom: 1px solid #333;
        margin-bottom: 30px;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        background: -webkit-linear-gradient(#4F46E5, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Custom Reading Box */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #151521;
        border-radius: 12px;
        padding: 30px;
        border: 1px solid #2d2d3d;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    st.error("⚠️ GOOGLE_API_KEY not found in .env file.")
    st.stop()

# ==========================================
# 2. CONSTANTS & PROMPTS
# ==========================================
MODEL_NAME = "gemini-3.5-flash-lite"

HUMAN_STYLE = """Write like a person, not like an AI:
- Vary your sentence length. Some short. Others longer, with a clause that earns its place.
- Use contractions (it's, don't, you'll) and talk straight to the reader as "you".
- Replace vague claims with a concrete example, a number, or a small story.
- Having an opinion is fine. Saying "I" is fine.
- Never use these words and phrases: "in today's fast-paced world", "delve", "moreover",
  "furthermore", "unlock", "leverage", "robust", "seamless", "game-changer",
  "it's worth noting", "navigate the landscape", "at the end of the day".
- Do not start every section the same way.
- Only use a bullet list when the content really is a list. Prefer paragraphs.
- Do not end with a summary of what you just said. End with one useful thought."""

OUTLINE_PROMPT = ChatPromptTemplate.from_template(
    "Write a short outline for a blog post.\n\nTopic: {topic}\nTone: {tone}\n\n"
    "Give me:\n- one opening line that makes the reader curious\n- 4 section headings\n"
    "- 5 key points the post must cover\n"
    "- If the topic is technical, include 2 practical code example placeholders. If non-technical, provide real-world examples.\n\n"
    "Just the outline. Do not write the post."
)

DRAFT_PROMPT = ChatPromptTemplate.from_template(
    "Write a blog post from this outline.\n\n{outline}\n\n" + HUMAN_STYLE + "\n\n"
                                                                            "Tone: {tone}\nOutput markdown with ### headings.\n"
                                                                            "Include clean code snippets if technical, else rich examples.\n"
)

POLISH_PROMPT = ChatPromptTemplate.from_template(
    "Improve this blog post without changing what it says.\n\n" + HUMAN_STYLE + "\n\n"
                                                                                "Also:\n- add a good # title at the top\n- keep the markdown\n\n"
                                                                                "Reply with the improved post only.\n\n{draft}"
)


# ==========================================
# 3. UTILITY FUNCTIONS
# ==========================================
def sanitize_markdown(text):
    """Cleans up rogue AI markdown to prevent layout breaks."""
    text = text.replace("\n\n\n", "\n\n")
    text = text.replace("```", "\n```\n")
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    return text.strip()


def run_blog_pipeline(topic, tone):
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7)

    with st.status("📝 Phase 1: Crafting the Outline...", expanded=False) as status:
        outline = (OUTLINE_PROMPT | llm | StrOutputParser()).invoke({"topic": topic, "tone": tone})
        status.update(label="✅ Phase 1: Outline Complete", state="complete", expanded=False)

    with st.status("✍️ Phase 2: Writing the Draft...", expanded=False) as status:
        draft = (DRAFT_PROMPT | llm | StrOutputParser()).invoke({"outline": outline, "tone": tone})
        status.update(label="✅ Phase 2: Draft Complete", state="complete", expanded=False)

    with st.status("✨ Phase 3: Polishing the Final Post...", expanded=False) as status:
        raw_final = (POLISH_PROMPT | llm | StrOutputParser()).invoke({"draft": draft})
        final_clean = sanitize_markdown(raw_final)
        status.update(label="✅ Phase 3: Polishing Complete", state="complete", expanded=False)

    return final_clean


# ==========================================
# 4. ADVANCED UI LAYOUT
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.markdown("Configure your AI writer below.")
    st.divider()

    topic = st.text_area("Blog Topic or Question", value="What is Docker?", height=180)
    tone = st.selectbox("Tone of Voice", ["Direct", "Normal", "Friendly", "Professional", "Humorous"])

    st.write("")
    generate_btn = st.button("🚀 Generate Blog")

    st.divider()

    st.markdown("### 🕰️ Recent Generations")
    if not st.session_state.history:
        st.caption("No blogs generated yet.")
    else:
        for item in reversed(st.session_state.history):
            st.caption(f"• {item['topic'][:25]}... ({item['tone']})")

    st.divider()
    st.caption(f"⚡ Powered by **{MODEL_NAME}**")

# --- MAIN PAGE ---
svg_logo = """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path><line x1="16" y1="8" x2="2" y2="22"></line><line x1="17.5" y1="15" x2="9" y2="15"></line></svg>"""

st.markdown(f"""
    <div class="header-box">
        {svg_logo}
        <h1 class="header-title">WriteFlow AI</h1>
    </div>
""", unsafe_allow_html=True)

# --- GENERATION LOGIC ---
if generate_btn:
    if not topic.strip():
        st.warning("Please enter a topic in the sidebar.")
    else:
        final_blog = run_blog_pipeline(topic, tone)

        st.session_state.history.append({
            "topic": topic,
            "tone": tone,
            "content": final_blog
        })

        st.session_state['current_blog'] = final_blog
        st.session_state['current_topic'] = topic

# --- OUTPUT SECTION ---
if 'current_blog' in st.session_state:
    st.success("🎉 Generation Complete!")

    # 1. Beautifully rendered Markdown Box
    with st.container(border=True):
        st.markdown(st.session_state['current_blog'])

    st.write("")

    # 2. Export Options (Now Full Width, perfectly aligned)
    st.markdown("#### 📥 Export & Share")

    safe_filename = st.session_state['current_topic'][:20].replace(' ', '_').lower()

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download Markdown (.md)",
            data=st.session_state['current_blog'],
            file_name=f"{safe_filename}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col2:
        st.download_button(
            label="📝 Download Text (.txt)",
            data=st.session_state['current_blog'],
            file_name=f"{safe_filename}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.write("")

    # 3. Raw Markdown safely tucked away for copying
    with st.expander("📋 View Raw Markdown (to Copy)"):
        st.code(st.session_state['current_blog'], language="markdown")
        st.caption("Click the copy icon in the top right of the code box to copy.")

else:
    # Empty state when app first loads
    st.info("👈 Enter a topic in the sidebar and click **Generate Blog** to get started.")