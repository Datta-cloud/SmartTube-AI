import streamlit as st
import time
import json
import re
from utils.youtube_helper import get_transcript, get_video_info
from utils.ai_helper import (generate_summary, generate_quiz, generate_notes,
                              generate_applications, generate_flashcards, chat_with_video)

st.set_page_config(page_title="YouTube AI Study Tool", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f0f1a; color: #e0e0e0; }
    h1 { color: #a78bfa; font-size: 2.5rem; text-align: center; }
    h2, h3 { color: #a78bfa; }
    .stButton>button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa);
        color: white; border: none; border-radius: 10px;
        padding: 10px 20px; font-size: 16px; font-weight: bold; width: 100%;
    }
    .stButton>button:hover { opacity: 0.85; }

    /* VIDEO PREVIEW */
    .video-preview {
        background: #1e1e2e; border-radius: 14px;
        padding: 16px; margin: 15px 0;
        border: 2px solid #7c3aed;
        display: flex; align-items: center; gap: 16px;
    }

    /* QUIZ */
    .quiz-box {
        background: #1e1e2e; border-radius: 12px;
        padding: 20px; margin: 15px 0;
        border-left: 4px solid #a78bfa; font-size: 16px;
    }
    .result-correct {
        background: #052e16; border-left: 4px solid #22c55e;
        border-radius: 8px; padding: 15px; margin: 10px 0;
    }
    .result-wrong {
        background: #2d0a0a; border-left: 4px solid #ef4444;
        border-radius: 8px; padding: 15px; margin: 10px 0;
    }
    .score-box {
        background: linear-gradient(135deg, #1e1e2e, #2d1b69);
        border-radius: 15px; padding: 30px;
        text-align: center; border: 2px solid #7c3aed; margin: 20px 0;
    }
    .timer-box {
        background: #1e1e2e; border-radius: 10px;
        padding: 12px 20px; margin: 10px 0;
        border: 2px solid #f59e0b; text-align: center;
        font-size: 22px; font-weight: bold; color: #f59e0b;
    }
    .timer-warning { border-color: #ef4444 !important; color: #ef4444 !important; }

    /* SUMMARY */
    .summary-point {
        background: #16213e; border-radius: 8px;
        padding: 14px 18px; margin: 8px 0;
        border-left: 3px solid #a78bfa;
        font-size: 15px; line-height: 1.7;
    }

    /* NOTES */
    .notes-section-heading {
        background: linear-gradient(135deg, #7c3aed, #4c1d95);
        color: white !important; border-radius: 10px;
        padding: 12px 20px; margin: 20px 0 10px 0;
        font-size: 18px; font-weight: bold;
    }
    .note-point {
        background: #1a1a2e; border-radius: 8px;
        padding: 14px 18px; margin: 7px 0;
        border-left: 3px solid #06b6d4;
        font-size: 15px; line-height: 1.75;
        display: flex; align-items: flex-start; gap: 10px;
    }
    .note-number {
        background: #06b6d4; color: #0f0f1a;
        border-radius: 50%; min-width: 24px; height: 24px;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 13px; margin-top: 1px;
    }

    /* CHAT */
    .chat-user {
        background: #2d1b69; border-radius: 12px 12px 4px 12px;
        padding: 12px 16px; margin: 8px 0 8px 60px;
        color: white; font-size: 15px;
    }
    .chat-ai {
        background: #1e1e2e; border-radius: 12px 12px 12px 4px;
        padding: 12px 16px; margin: 8px 60px 8px 0;
        border-left: 3px solid #a78bfa;
        color: #e0e0e0; font-size: 15px; line-height: 1.7;
    }

    /* APPS */
    .app-card {
        background: #1a1a2e; border-radius: 12px;
        padding: 20px; margin: 10px 0; border: 1px solid #374151;
    }
    .export-box {
        background: #1e1e2e; border-radius: 12px;
        padding: 20px; margin: 15px 0;
        border: 2px dashed #7c3aed;
    }

    .stTextInput>div>div>input {
        background-color: #1e1e2e; color: white;
        border: 2px solid #7c3aed; border-radius: 8px;
    }
    .stRadio>div { color: #e0e0e0; }
    div[data-testid="stRadio"] label { font-size: 15px !important; }
    .stTabs [data-baseweb="tab"] { color: #a78bfa; font-size: 16px; font-weight: bold; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #7c3aed; }
    div[data-testid="stSelectbox"] { color: white; }
</style>
""", unsafe_allow_html=True)

# ========== HELPER FUNCTIONS ==========

def generate_notes_pdf_html(notes, title="Study Notes"):
    sections_html = ""
    if notes and isinstance(notes[0], dict):
        for s in notes:
            heading = s.get("section", "Section")
            points = s.get("points", [])
            pts_html = "".join([f"<li style='margin:8px 0; line-height:1.7;'>{p}</li>" for p in points])
            sections_html += f"""
            <div style='margin:20px 0; background:white; border-radius:10px;
                        padding:20px; border-left:5px solid #7c3aed; box-shadow:0 2px 8px rgba(0,0,0,0.08);'>
                <h3 style='color:#7c3aed; margin:0 0 12px 0;'>{heading}</h3>
                <ul style='margin:0; padding-left:20px; color:#1a1a2e;'>{pts_html}</ul>
            </div>"""
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title></head>
<body style='font-family:Segoe UI,Arial,sans-serif; background:#f0f2f5; padding:30px; color:#1a1a2e;'>
<div style='background:linear-gradient(135deg,#7c3aed,#a78bfa); color:white; padding:25px 30px;
     border-radius:12px; text-align:center; margin-bottom:25px;'>
  <h1 style='margin:0; font-size:24px;'>📒 {title}</h1>
  <p style='margin:5px 0 0 0; opacity:0.85;'>AI Generated Study Notes</p>
</div>
<div style='background:#fff3cd; padding:12px 16px; border-radius:8px; margin-bottom:20px;
     border-left:4px solid #ffc107; font-size:14px;'>
  💡 <b>To save as PDF:</b> Press Ctrl+P → Save as PDF → Save
</div>
{sections_html}
</body></html>"""
    return html

def generate_quiz_pdf_html(quiz_data, title="Quiz"):
    questions_html = ""
    for i, q in enumerate(quiz_data):
        opts = "".join([f"<div style='margin:6px 0; padding:8px 12px; background:#f8f9fa; border-radius:6px; border:1px solid #dee2e6;'>⬜ &nbsp; {o}</div>" for o in q["options"]])
        questions_html += f"""<div style='margin:20px 0; padding:20px; background:white; border-radius:10px;
             border-left:4px solid #7c3aed; box-shadow:0 2px 8px rgba(0,0,0,0.08);'>
            <p style='font-size:16px; font-weight:bold; color:#1a1a2e; margin:0 0 12px 0;'>Q{i+1}. {q['question']}</p>
            {opts}</div>"""
    answer_key = "".join([f"<p style='margin:4px 0;'><b>Q{i+1}:</b> {q['answer']}</p>" for i, q in enumerate(quiz_data)])
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title></head>
<body style='font-family:Segoe UI,Arial,sans-serif; background:#f0f2f5; padding:30px;'>
<div style='background:linear-gradient(135deg,#7c3aed,#a78bfa); color:white; padding:25px 30px;
     border-radius:12px; text-align:center; margin-bottom:25px;'>
  <h1 style='margin:0; font-size:24px;'>🧠 {title}</h1>
  <p style='margin:5px 0 0 0; opacity:0.85;'>{len(quiz_data)} Questions</p>
</div>
<div style='background:#fff3cd; padding:12px 16px; border-radius:8px; margin-bottom:20px;
     border-left:4px solid #ffc107; font-size:14px;'>
  💡 <b>To save as PDF:</b> Press Ctrl+P → Save as PDF → Save
</div>
{questions_html}
<div style='background:#e8f5e9; border-radius:10px; padding:20px; margin-top:30px; border:2px solid #4caf50;'>
  <h3 style='color:#2e7d32; margin-top:0;'>✅ Answer Key</h3>{answer_key}
</div></body></html>"""
    return html

# ========== MAIN APP ==========

st.markdown("# 🎓 YouTube AI Study Tool")
st.markdown("<p style='text-align:center; color:#9ca3af;'>Paste any YouTube link → Get Summary, Quiz, Notes & More!</p>", unsafe_allow_html=True)
st.divider()

# --- Language & Settings Row ---
col_url, col_lang = st.columns([4, 1])
with col_url:
    url = st.text_input("🔗 Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
with col_lang:
    language = st.selectbox("🌐 Language", ["English", "Hindi", "Marathi"], key="lang")

# --- Video Preview ---
if url and "video_info" not in st.session_state:
    info = get_video_info(url)
    if info:
        st.session_state["video_info"] = info

if "video_info" in st.session_state and url:
    info = st.session_state["video_info"]
    c1, c2 = st.columns([1, 3])
    with c1:
        if info.get("thumbnail"):
            st.image(info["thumbnail"], width=280)
    with c2:
        st.markdown(f"### 🎬 {info.get('title', 'Video')}")
        st.markdown(f"<p style='color:#9ca3af;'>👤 {info.get('author', '')} &nbsp;|&nbsp; ✅ Video found — ready to analyse!</p>", unsafe_allow_html=True)

if st.button("🚀 Analyse Video"):
    if not url:
        st.warning("Please enter a YouTube URL first!")
    else:
        with st.spinner("⏳ Fetching video info..."):
            transcript = get_transcript(url)
        if not transcript:
            st.error("❌ Invalid URL.")
        else:
            st.session_state["transcript"] = transcript
            st.session_state["url"] = url
            st.session_state["language"] = language
            st.session_state["quiz_submitted"] = False
            st.session_state["user_answers"] = {}
            st.session_state["chat_history"] = []
            st.session_state["quiz_start_time"] = None
            for k in ["flashcards", "show_pdf", "show_form", "pdf_html", "form_text", "notes_pdf_html"]:
                st.session_state.pop(k, None)

            with st.spinner("🤖 Generating Summary..."):
                st.session_state["summary"] = generate_summary(transcript, language)
            with st.spinner("📝 Creating Quiz..."):
                st.session_state["quiz"] = generate_quiz(transcript, language, "Medium")
            with st.spinner("📚 Making Notes..."):
                st.session_state["notes"] = generate_notes(transcript, language)
            with st.spinner("💡 Finding Applications..."):
                st.session_state["applications"] = generate_applications(transcript, language)
            st.rerun()

# ========== TABS ==========
if "summary" in st.session_state:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Summary", "🧠 Quiz", "📒 Notes", "💡 Applications", "🎯 Flashcards", "💬 Chat"
    ])

    # ---- TAB 1: SUMMARY ----
    with tab1:
        lang = st.session_state.get("language", "English")
        st.markdown(f"## 📋 Video Summary &nbsp; <span style='font-size:14px; color:#9ca3af;'>({lang})</span>", unsafe_allow_html=True)
        summary = st.session_state['summary']
        lines = [l.strip() for l in summary.split('\n') if l.strip()]
        for line in lines:
            clean = line.lstrip('*-•123456789. ').strip()
            if clean:
                st.markdown(f"<div class='summary-point'>💡 {clean}</div>", unsafe_allow_html=True)

    # ---- TAB 2: QUIZ ----
    with tab2:
        st.markdown("## 🧠 Test Yourself")
        quiz_data = st.session_state.get("quiz", [])

        # Difficulty + regenerate row
        dcol1, dcol2 = st.columns([2, 1])
        with dcol1:
            difficulty = st.selectbox("🎯 Difficulty Level", ["Easy", "Medium", "Hard"], index=1, key="difficulty")
        with dcol2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Generate New Quiz"):
                with st.spinner("Generating quiz..."):
                    st.session_state["quiz"] = generate_quiz(
                        st.session_state["transcript"],
                        st.session_state.get("language", "English"),
                        difficulty
                    )
                st.session_state["quiz_submitted"] = False
                st.session_state["user_answers"] = {}
                st.session_state["quiz_start_time"] = None
                st.rerun()

        if not quiz_data:
            st.error("Quiz could not be generated.")
        else:
            # Export buttons
            st.markdown("<div class='export-box'>", unsafe_allow_html=True)
            st.markdown("### 📤 Export Quiz")
            ecol1, ecol2 = st.columns(2)
            with ecol1:
                if st.button("📄 Save Quiz as PDF"):
                    vt = st.session_state.get("transcript", "")
                    title = vt.split("::TITLE::")[1] if "::TITLE::" in vt else "Quiz"
                    st.session_state["pdf_html"] = generate_quiz_pdf_html(quiz_data, title)
                    st.session_state["show_pdf"] = True
            with ecol2:
                if st.button("📋 Export for Google Forms"):
                    vt = st.session_state.get("transcript", "")
                    title = vt.split("::TITLE::")[1] if "::TITLE::" in vt else "Quiz"
                    txt = f"QUIZ: {title}\n{'='*50}\n\n"
                    for i, q in enumerate(quiz_data):
                        txt += f"Q{i+1}: {q['question']}\n"
                        for j, o in enumerate(q["options"]):
                            mark = "✓ " if o == q["answer"] else "   "
                            txt += f"  {mark}{chr(65+j)}: {o}\n"
                        txt += f"Answer: {q['answer']}\n{'-'*40}\n\n"
                    st.session_state["form_text"] = txt
                    st.session_state["show_form"] = True
            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.get("show_pdf"):
                st.download_button("⬇️ Download Quiz HTML → Open in Browser → Ctrl+P → Save as PDF",
                    data=st.session_state["pdf_html"], file_name="quiz.html", mime="text/html", use_container_width=True)
                st.info("💡 Open downloaded file in Chrome → Ctrl+P → Save as PDF")
                if st.button("✖ Close", key="close_pdf"): st.session_state["show_pdf"] = False; st.rerun()

            if st.session_state.get("show_form"):
                st.download_button("⬇️ Download Questions for Google Forms",
                    data=st.session_state["form_text"], file_name="quiz_google_forms.txt", mime="text/plain", use_container_width=True)
                st.link_button("🔗 Open Google Forms", "https://forms.google.com", use_container_width=True)
                if st.button("✖ Close", key="close_form"): st.session_state["show_form"] = False; st.rerun()

            st.markdown("---")

            # QUIZ FORM
            if not st.session_state.get("quiz_submitted", False):
                # Start timer when quiz begins
                if st.session_state.get("quiz_start_time") is None:
                    st.session_state["quiz_start_time"] = time.time()

                # Timer display
                elapsed = time.time() - st.session_state["quiz_start_time"]
                total_seconds = 15 * 60  # 15 minutes
                remaining = max(0, total_seconds - int(elapsed))
                mins = remaining // 60
                secs = remaining % 60
                timer_class = "timer-box timer-warning" if remaining < 120 else "timer-box"
                st.markdown(f"<div class='{timer_class}'>⏱️ Time Remaining: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)

                if remaining == 0:
                    st.warning("⏰ Time's up! Auto-submitting...")
                    st.session_state["quiz_submitted"] = True
                    st.rerun()

                with st.form("quiz_form"):
                    user_answers = {}
                    for i, q in enumerate(quiz_data):
                        st.markdown(f"<div class='quiz-box'><b>Q{i+1}. {q['question']}</b></div>", unsafe_allow_html=True)
                        ans = st.radio(f"q{i}", options=q["options"], index=None,
                                       key=f"q_{i}", label_visibility="collapsed")
                        user_answers[i] = ans
                    submitted = st.form_submit_button("✅ Submit Quiz")
                    if submitted:
                        unanswered = [i+1 for i, a in user_answers.items() if a is None]
                        if unanswered:
                            st.warning(f"Please answer all questions! Pending: Q{unanswered}")
                        else:
                            st.session_state["user_answers"] = user_answers
                            st.session_state["quiz_submitted"] = True
                            st.rerun()
            else:
                user_answers = st.session_state["user_answers"]
                score = 0
                total = len(quiz_data)
                wrong_topics = []
                for i, q in enumerate(quiz_data):
                    user_ans = user_answers.get(i, "")
                    correct = q["answer"]
                    if user_ans == correct:
                        score += 1
                        st.markdown(f"""<div class='result-correct'>✅ <b>Q{i+1}. {q['question']}</b><br>
                            <span style='color:#86efac;'>Your answer: {user_ans} ✔</span></div>""", unsafe_allow_html=True)
                    else:
                        wrong_topics.append(q.get("topic", q["question"][:40]))
                        st.markdown(f"""<div class='result-wrong'>❌ <b>Q{i+1}. {q['question']}</b><br>
                            <span style='color:#fca5a5;'>Your answer: {user_ans}</span><br>
                            <span style='color:#86efac;'>✔ Correct: {correct}</span></div>""", unsafe_allow_html=True)

                percent = int((score / total) * 100)
                emoji = "🏆" if percent >= 80 else "👍" if percent >= 50 else "📖"
                st.markdown(f"""<div class='score-box'>
                    <div style='font-size:3rem;'>{emoji}</div>
                    <h2 style='color:white;'>Score: {score} / {total}</h2>
                    <h3 style='color:#a78bfa;'>{percent}%</h3>
                </div>""", unsafe_allow_html=True)

                if wrong_topics:
                    st.markdown("### 🔧 Areas to Improve")
                    for t in wrong_topics:
                        st.markdown(f"<div class='summary-point'>📌 {t}</div>", unsafe_allow_html=True)

                if st.button("🔁 Retake Quiz — New Questions"):
                    with st.spinner("Generating new questions..."):
                        st.session_state["quiz"] = generate_quiz(
                            st.session_state["transcript"],
                            st.session_state.get("language", "English"),
                            difficulty
                        )
                    st.session_state["quiz_submitted"] = False
                    st.session_state["user_answers"] = {}
                    st.session_state["quiz_start_time"] = None
                    st.rerun()

    # ---- TAB 3: NOTES ----
    with tab3:
        st.markdown("## 📒 Study Notes")
        notes = st.session_state.get("notes", [])
        section_icons = ["🔵", "🟢", "🟡", "🔴", "🟣", "🟠"]

        # Download Notes PDF button
        if notes:
            vt = st.session_state.get("transcript", "")
            title = vt.split("::TITLE::")[1] if "::TITLE::" in vt else "Study Notes"
            notes_html = generate_notes_pdf_html(notes, title)
            st.download_button("📄 Download Notes as PDF",
                data=notes_html, file_name="study_notes.html",
                mime="text/html", use_container_width=False)
            st.markdown("---")

        if notes and isinstance(notes[0], dict):
            for s_idx, section in enumerate(notes):
                icon = section_icons[s_idx % len(section_icons)]
                heading = section.get("section", f"Section {s_idx+1}")
                points = section.get("points", [])
                st.markdown(f"<div class='notes-section-heading'>{icon} &nbsp; {heading}</div>", unsafe_allow_html=True)
                for p_idx, point in enumerate(points):
                    clean = point.lstrip('*-•123456789. ').strip()
                    st.markdown(f"""<div class='note-point'>
                        <div class='note-number'>{p_idx+1}</div>
                        <div>{clean}</div></div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        elif notes:
            col1, col2 = st.columns(2)
            for i, note in enumerate(notes):
                clean = str(note).lstrip('*-•123456789. ').strip()
                with (col1 if i % 2 == 0 else col2):
                    st.markdown(f"""<div class='note-point'>
                        <div class='note-number'>{i+1}</div><div>{clean}</div></div>""", unsafe_allow_html=True)
        else:
            st.info("Notes could not be generated.")

    # ---- TAB 4: APPLICATIONS ----
    with tab4:
        st.markdown("## 💡 Real-World Applications")
        apps = st.session_state.get("applications", [])
        if apps:
            for app in apps:
                st.markdown(f"""<div class='app-card'>
                    <h4 style='color:#a78bfa; margin:0 0 8px 0;'>🔹 {app['title']}</h4>
                    <p style='color:#d1d5db; line-height:1.7; margin:0;'>{app['description']}</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Applications could not be generated.")

    # ---- TAB 5: FLASHCARDS ----
    with tab5:
        st.markdown("## 🎯 Quick Flashcards")
        st.markdown("<p style='color:#9ca3af;'>Click on a card to reveal the answer!</p>", unsafe_allow_html=True)
        if "flashcards" not in st.session_state:
            with st.spinner("Generating flashcards..."):
                st.session_state["flashcards"] = generate_flashcards(st.session_state.get("transcript", ""))
        for i, card in enumerate(st.session_state.get("flashcards", [])):
            with st.expander(f"❓ {card['question']}"):
                st.markdown(f"<p style='color:#86efac; font-size:16px; padding:10px;'>💡 {card['answer']}</p>", unsafe_allow_html=True)

    # ---- TAB 6: CHAT ----
    with tab6:
        st.markdown("## 💬 Chat with Video")
        st.markdown("<p style='color:#9ca3af;'>Ask anything about this video's topic!</p>", unsafe_allow_html=True)

        # Init chat history
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Show chat history
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

        # Quick question suggestions
        st.markdown("**💡 Quick Questions:**")
        qcol1, qcol2, qcol3 = st.columns(3)
        suggestions = [
            "Explain this topic in simple words",
            "What are the most important points?",
            "Give me a real-life example",
            "What should I study next?",
            "Summarize in 3 lines",
            "What are common mistakes to avoid?"
        ]
        for i, (col, sug) in enumerate(zip([qcol1, qcol2, qcol3, qcol1, qcol2, qcol3], suggestions)):
            with col:
                if st.button(sug, key=f"sug_{i}"):
                    st.session_state["chat_input_prefill"] = sug

        # Chat input
        user_q = st.text_input(
            "Ask a question...",
            value=st.session_state.pop("chat_input_prefill", ""),
            placeholder="e.g. Explain mitosis in simple words",
            key="chat_input"
        )

        if st.button("📨 Send", key="send_chat"):
            if user_q.strip():
                st.session_state["chat_history"].append({"role": "user", "content": user_q})
                with st.spinner("🤖 Thinking..."):
                    reply = chat_with_video(
                        st.session_state.get("transcript", ""),
                        st.session_state["chat_history"],
                        st.session_state.get("language", "English")
                    )
                st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                st.rerun()

        if st.session_state.get("chat_history"):
            if st.button("🗑️ Clear Chat"):
                st.session_state["chat_history"] = []
                st.rerun()
