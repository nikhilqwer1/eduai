import streamlit as st
from streamlit_mic_recorder import mic_recorder

from auth_manager import register_user, login_user, save_learning_record, get_user_history
from rag_engine import DocumentEngine
from gemini_engine import generate_structured_lesson, generate_diagnostic_report
from audio_engine import generate_scene_audio
from avatar_engine import generate_avatar_video
from stt_engine import transcribe_audio_bytes

st.set_page_config(
    page_title="EduAI Studio | Master AI Teacher",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# ============================================================
# MODERN DESIGN SYSTEM & CUSTOM HTML/CSS INJECTION
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* 1. Reset Default Streamlit Boilerplate */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem 4rem 2rem !important; max-width: 1400px; }
    * { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }

    /* 2. Custom Navigation Bar */
    .custom-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        padding: 0.9rem 1.75rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .brand-flex { display: flex; align-items: center; gap: 12px; }
    .brand-badge-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #4F46E5, #2563EB);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        font-size: 1.25rem;
        font-weight: bold;
    }
    .brand-title { font-size: 1.3rem; font-weight: 800; color: #0F172A; line-height: 1.1; }
    .brand-tag { font-size: 0.72rem; color: #4F46E5; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }

    /* 3. Hero Cards & Surface Containers */
    .hero-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 2.2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
        margin-bottom: 2rem;
    }
    .hero-title-box { text-align: center; max-width: 750px; margin: 0 auto 1.75rem auto; }
    .hero-badge {
        display: inline-block;
        background-color: #EEF2FF;
        color: #4F46E5;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 0.75rem;
        border: 1px solid #E0E7FF;
    }
    .hero-title-box h1 { font-size: 2.1rem; font-weight: 800; color: #0F172A; line-height: 1.25; margin-bottom: 6px; }
    .hero-title-box p { color: #64748B; font-size: 0.98rem; }

    /* 4. Classroom Visual Board */
    .board-header {
        background: #0F172A;
        color: #FFFFFF;
        padding: 10px 16px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        font-weight: 700;
        font-size: 0.88rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .board-mode-tag {
        background: #1E293B;
        color: #38BDF8;
        font-size: 0.72rem;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* 5. Concept Checkpoints */
    .checkpoint-container {
        background: #F8FAFC;
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }
    .checkpoint-title { font-size: 1.05rem; font-weight: 700; color: #1E1B4B; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# Session States
if "user" not in st.session_state:
    st.session_state.user = None
if "doc_engine" not in st.session_state:
    st.session_state.doc_engine = DocumentEngine()
if "lesson_plan" not in st.session_state:
    st.session_state.lesson_plan = None
if "scene_idx" not in st.session_state:
    st.session_state.scene_idx = 0
if "checkpoints_state" not in st.session_state:
    st.session_state.checkpoints_state = {}
if "completed" not in st.session_state:
    st.session_state.completed = False
if "voice_answer_text" not in st.session_state:
    st.session_state.voice_answer_text = ""
if "media_mode" not in st.session_state:
    st.session_state.media_mode = "🎥 Video + Visuals"

# ============================================================
# TOP NAVBAR
# ============================================================
user_name = st.session_state.user["name"] if st.session_state.user else "Guest Student"
st.markdown(f"""
<div class="custom-navbar">
    <div class="brand-flex">
        <div class="brand-badge-icon">🎓</div>
        <div>
            <div class="brand-title">EduAI Studio</div>
            <div class="brand-tag">Master Class Platform</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 14px;">
        <span style="font-weight: 600; font-size: 0.9rem; color: #334155;">🧑‍🎓 {user_name}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 1. AUTHENTICATION VIEW
# ============================================================
if not st.session_state.user:
    st.markdown("""
    <div class="hero-container" style="max-width: 520px; margin: 2rem auto;">
        <div class="hero-title-box">
            <span class="hero-badge">Student Access</span>
            <h1>Welcome to EduAI</h1>
            <p>Sign in to access deep-dive topics, checkpoint records, and progress analytics.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 1.6, 1])
    with auth_col2:
        tab_login, tab_signup = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            u = st.text_input("Username", key="l_user")
            p = st.text_input("Password", type="password", key="l_pass")
            if st.button("Sign In to Classroom", type="primary", use_container_width=True):
                name = login_user(u, p)
                if name:
                    st.session_state.user = {"username": u, "name": name}
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tab_signup:
            fn = st.text_input("Full Name", key="s_name")
            su = st.text_input("Choose Username", key="s_user")
            sp = st.text_input("Choose Password", type="password", key="s_pass")
            if st.button("Register Account", use_container_width=True):
                if fn and su and sp:
                    ok, msg = register_user(su, sp, fn)
                    if ok:
                        st.success(msg)
                    else:
                        st.warning(msg)
                else:
                    st.warning("Please fill all fields.")

# ============================================================
# 2. MAIN LMS INTERFACE
# ============================================================
else:
    # --------------------------------------------------------
    # VIEW A: SETUP & DASHBOARD (NO SIDEBAR)
    # --------------------------------------------------------
    if not st.session_state.lesson_plan and not st.session_state.completed:
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title-box">
                <span class="hero-badge">⚡ Powered by Gemini 3.6 Flash & Whisper STT</span>
                <h1>What topic would you like to master today?</h1>
                <p>Deep pedagogical breakdowns from first principles with synchronized video chalkboard visuals.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Topic Query & Learning Mode
        c_top1, c_top2 = st.columns([3, 1.2])
        with c_top1:
            topic = st.text_input("🔍 Topic / Subject Search", placeholder="e.g. Dynamic Programming, Transformer Attention, B+ Trees...")
        with c_top2:
            st.session_state.media_mode = st.radio(
                "Experience Format",
                ["🎥 Video + Visuals", "🎧 Audio Only"],
                horizontal=True
            )

        # In-depth Configuration Parameters
        p1, p2, p3 = st.columns(3)
        with p1:
            level = st.selectbox("Proficiency Level", ["Beginner (Intuition)", "Intermediate (Rigorous)", "Advanced (Proof & Edge Cases)"])
        with p2:
            duration = st.selectbox("Target Duration", [10, 15, 30], format_func=lambda x: f"{x} Minutes")
        with p3:
            language = st.selectbox(
                "Explanation Language",
                ["Hinglish", "Hindi", "English", "Bengali", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada", "Malayalam", "Punjabi"]
            )

        # Optional RAG Context
        with st.expander("📄 Optional: Index Syllabus / Lecture Notes PDF"):
            uploaded_file = st.file_uploader("Upload reference PDF/TXT", type=["pdf", "txt"])
            if uploaded_file and st.button("Index Material"):
                with st.spinner("Processing embeddings into vector store..."):
                    status = st.session_state.doc_engine.process_file(uploaded_file)
                    st.success(status)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start Interactive Masterclass 🚀", type="primary", use_container_width=True):
            if not topic and not uploaded_file:
                st.warning("Please specify a topic or attach a lecture PDF.")
            else:
                with st.spinner("AI Teacher is preparing the deep-dive curriculum..."):
                    ctx = st.session_state.doc_engine.retrieve_context(topic or "Summary")
                    st.session_state.lesson_plan = generate_structured_lesson(
                        topic=topic or "Uploaded Notes",
                        context=ctx,
                        level=level,
                        time_mins=duration,
                        language=language
                    )
                    st.session_state.scene_idx = 0
                    st.session_state.checkpoints_state = {}
                    st.session_state.completed = False
                    st.session_state.voice_answer_text = ""
                    st.rerun()

        # Mastery History Records
        st.markdown("---")
        st.markdown("#### 📈 Your Mastery Record")
        history = get_user_history(st.session_state.user["username"])
        if history:
            h_cols = st.columns(3)
            for i, rec in enumerate(history[:3]):
                with h_cols[i]:
                    st.info(f"**{rec[0]}**\n\nScore: **{rec[1]:.0f}%**\n\n_{rec[3]}_")
        else:
            st.caption("No completed lessons yet. Start your first session above!")

    # --------------------------------------------------------
    # VIEW B: ACTIVE TEACHING WORKSPACE
    # --------------------------------------------------------
    elif st.session_state.lesson_plan and not st.session_state.completed:
        plan = st.session_state.lesson_plan
        scenes = plan.scenes
        idx = st.session_state.scene_idx
        scene = scenes[idx]

        # Top Bar & Progress
        h_left, h_right = st.columns([5, 1])
        with h_left:
            st.markdown(f"### 📖 {plan.lesson_title}")
            st.progress((idx + 1) / len(scenes), text=f"Scene {idx + 1} of {len(scenes)}: {scene.title}")
        with h_right:
            if st.button("Change Topic 🔄", use_container_width=True):
                st.session_state.lesson_plan = None
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Two-Column Media & Blackboard Split
        media_col, board_col = st.columns([1.1, 1.4])

        with media_col:
            st.markdown(f"#### 🎙️ Virtual Educator ({st.session_state.media_mode})")
            audio_path = generate_scene_audio(scene.avatar_speech, plan.language)

            if "Video" in st.session_state.media_mode:
                with st.spinner("Rendering dynamic chalkboard video..."):
                    video_path = generate_avatar_video(
                        audio_path=audio_path,
                        title=scene.title,
                        visual_type=scene.visual_type,
                        visual_content=scene.visual_content
                    )
                st.video(video_path, autoplay=True)
            else:
                st.audio(audio_path, format="audio/mp3", autoplay=True)
                st.info("🎧 Audio streaming mode active.")

            with st.expander("📝 Spoken Script Transcript"):
                st.write(scene.avatar_speech)

        with board_col:
            st.markdown(f"""
            <div class="board-header">
                <span>📋 INTERACTIVE BLACKBOARD</span>
                <span class="board-mode-tag">{scene.visual_type.upper()}</span>
            </div>
            """, unsafe_allow_html=True)

            if scene.visual_type == "code":
                st.code(scene.visual_content, language="python")
            elif scene.visual_type == "formula":
                st.latex(scene.visual_content)
            else:
                st.markdown(scene.visual_content)

        # Checkpoints with Voice STT & MCQ
        checkpoints = [cp for cp in plan.checkpoints if cp.trigger_after_scene_id == scene.scene_id]
        can_proceed = True

        if checkpoints:
            cp = checkpoints[0]
            st.markdown("<div class='checkpoint-container'>", unsafe_allow_html=True)
            st.markdown(f"<div class='checkpoint-title'>❓ Concept Checkpoint: {cp.question}</div>", unsafe_allow_html=True)

            answering_mode = st.radio("Response Mode:", ["🎙️ Voice Answer (Whisper STT)", "📝 Choose Option"], horizontal=True)

            if answering_mode == "🎙️ Voice Answer (Whisper STT)":
                st.caption("Press record and explain your answer:")
                rec = mic_recorder(start_prompt="🔴 Start Speaking", stop_prompt="⏹️ Stop", key=f"rec_{cp.checkpoint_id}")

                if rec and "bytes" in rec:
                    with st.spinner("Transcribing your explanation..."):
                        st.session_state.voice_answer_text = transcribe_audio_bytes(rec["bytes"])

                if st.session_state.voice_answer_text:
                    st.info(f"🎙️ **Detected Speech:** \"{st.session_state.voice_answer_text}\"")

                if st.button("Evaluate Voice Response"):
                    user_text = st.session_state.voice_answer_text.lower()
                    correct = cp.correct_answer.lower()
                    if correct in user_text or any(w in user_text for w in correct.split()):
                        st.session_state.checkpoints_state[cp.checkpoint_id] = True
                        st.success("🎯 Correct! Excellent conceptual clarity.")
                    else:
                        st.session_state.checkpoints_state[cp.checkpoint_id] = False
                        st.warning(f"💡 Simple Explanation: {cp.explanation_on_fail}")
            else:
                choice = st.radio("Options:", cp.options, key=f"q_{cp.checkpoint_id}")
                if st.button("Submit Selected Option"):
                    if choice == cp.correct_answer:
                        st.session_state.checkpoints_state[cp.checkpoint_id] = True
                        st.success("🎯 Correct! Well done.")
                    else:
                        st.session_state.checkpoints_state[cp.checkpoint_id] = False
                        st.warning(f"💡 Explanation: {cp.explanation_on_fail}")

            st.markdown("</div>", unsafe_allow_html=True)

            if not st.session_state.checkpoints_state.get(cp.checkpoint_id, False):
                can_proceed = False

        # Navigation Controls
        st.markdown("<br>", unsafe_allow_html=True)
        nav1, nav2, _ = st.columns([1, 1, 4])
        with nav1:
            if st.button("⬅️ Previous", disabled=(idx == 0)):
                st.session_state.scene_idx -= 1
                st.session_state.voice_answer_text = ""
                st.rerun()
        with nav2:
            if idx < len(scenes) - 1:
                if st.button("Next Scene ➡️", disabled=not can_proceed):
                    st.session_state.scene_idx += 1
                    st.session_state.voice_answer_text = ""
                    st.rerun()
            else:
                if st.button("Finish & View Scorecard 📝", disabled=not can_proceed, type="primary"):
                    st.session_state.completed = True
                    st.rerun()

    # --------------------------------------------------------
    # VIEW C: DIAGNOSTIC SCORECARD
    # --------------------------------------------------------
    elif st.session_state.completed:
        st.balloons()
        st.subheader("📊 Session Assessment & Diagnostics")

        with st.spinner("Analyzing mastery performance..."):
            summary_info = f"Topic: {st.session_state.lesson_plan.lesson_title}, Passed Checkpoints: {sum(1 for v in st.session_state.checkpoints_state.values() if v)} / {len(st.session_state.lesson_plan.checkpoints)}"
            report = generate_diagnostic_report(st.session_state.lesson_plan.lesson_title, summary_info)
            save_learning_record(st.session_state.user["username"], st.session_state.lesson_plan.lesson_title, report.score_percentage, report.weak_concepts)

        c1, c2 = st.columns(2)
        with c1:
            st.metric(label="Overall Topic Mastery", value=f"{report.score_percentage:.1f}%")
            st.markdown("##### ✅ Mastered Concepts")
            for m in report.mastered_concepts:
                st.write(f"• {m}")

        with c2:
            st.markdown("##### ⚠️ Revision Focus Areas")
            for w in report.weak_concepts:
                st.write(f"• {w}")
            st.markdown("##### 🚀 Recommended Next Step")
            st.info(report.suggested_next_topic)

        st.markdown(f"**📚 Revision Guidance:**\n{report.recommended_revision_plan}")

        if st.button("Return to Master Dashboard 🏠", type="primary"):
            st.session_state.lesson_plan = None
            st.session_state.completed = False
            st.rerun()