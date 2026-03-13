import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Interview Practice", page_icon="🤖", layout="wide")

# Refresh every second for timer
st_autorefresh(interval=1000, key="timer")

# ---------------- CSS ----------------
st.markdown("""
<style>

.main-title{
text-align:center;
font-size:42px;
font-weight:bold;
margin-bottom:10px;
}

.subtitle{
text-align:center;
font-size:18px;
color:gray;
margin-bottom:30px;
}

.question-card{
background:white;
padding:25px;
border-radius:12px;
box-shadow:0px 2px 10px rgba(0,0,0,0.1);
margin-bottom:20px;
color:black !important;
}

.result-card{
background:white;
padding:25px;
border-radius:12px;
box-shadow:0px 2px 10px rgba(0,0,0,0.1);
margin-top:20px;
text-align:center;
color:black !important;
}

.timer{
color:red;
font-weight:bold;
font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "scores" not in st.session_state:
    st.session_state.scores = []

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

# ---------------- LOAD QUESTIONS ----------------
data = pd.read_csv("questions.csv")

questions = data["question"].tolist()
opt1 = data["option1"].tolist()
opt2 = data["option2"].tolist()
opt3 = data["option3"].tolist()
opt4 = data["option4"].tolist()
correct_answers = data["correct_answer"].tolist()

TOTAL_QUESTIONS = min(5, len(questions))

# ---------------- HOME PAGE ----------------
if st.session_state.page == "home":

    st.markdown('<div class="main-title">🤖 AI Interview Practice Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Practice real interview questions and test your knowledge</div>', unsafe_allow_html=True)

    name = st.text_input("Enter your name")

    if st.button("Start Interview"):
        if name.strip() == "":
            st.warning("Please enter your name")
        else:
            st.session_state.username = name
            st.session_state.page = "interview"
            st.session_state.current_q = 0
            st.session_state.scores = []
            st.session_state.start_time = time.time()
            st.rerun()

    st.stop()

# ---------------- INTERVIEW PAGE ----------------
if st.session_state.page == "interview":

    # -------- Progress Tracker --------
    st.markdown("### Question Progress")

    cols = st.columns(TOTAL_QUESTIONS)

    for i in range(TOTAL_QUESTIONS):
        if i < len(st.session_state.scores):
            cols[i].success(i + 1)
        else:
            cols[i].write(i + 1)

    # -------- End Interview --------
    if st.session_state.current_q >= TOTAL_QUESTIONS:

        st.session_state.page = "result"
        st.rerun()

    # -------- Show Question --------
    q = questions[st.session_state.current_q]

    st.markdown(f"""
    <div class="question-card">
    <h3>Question {st.session_state.current_q + 1} of {TOTAL_QUESTIONS}</h3>
    <p>{q}</p>
    </div>
    """, unsafe_allow_html=True)

    # -------- Timer --------
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(60 - elapsed, 0)

    st.markdown(f'<p class="timer">⏱ Time Remaining: {remaining} seconds</p>', unsafe_allow_html=True)

    # -------- Options --------
    options = [
        opt1[st.session_state.current_q],
        opt2[st.session_state.current_q],
        opt3[st.session_state.current_q],
        opt4[st.session_state.current_q],
    ]

    answer = st.radio("Select your answer:", options)

    # -------- Submit --------
    if st.button("Submit Answer"):

        correct = correct_answers[st.session_state.current_q]

        if answer == correct:
            st.success("✅ Correct Answer")
            score = 10
        else:
            st.error("❌ Incorrect Answer")
            score = 0

        st.session_state.scores.append(score)

        st.info(f"Correct Answer: {correct}")

    # -------- Navigation --------
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Next Question"):
            st.session_state.current_q += 1
            st.session_state.start_time = time.time()
            st.rerun()

    with col2:
        if st.button("Skip"):
            st.session_state.current_q += 1
            st.session_state.start_time = time.time()
            st.rerun()

# ---------------- RESULT PAGE ----------------
if st.session_state.page == "result":

    st.markdown("""
    <div class="result-card">
    <h2>📊 Interview Result</h2>
    </div>
    """, unsafe_allow_html=True)

    total = TOTAL_QUESTIONS
    answered = len(st.session_state.scores)
    correct = sum(1 for s in st.session_state.scores if s == 10)

    score_percent = int((correct / total) * 100)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Questions", total)
    col2.metric("Answered", answered)
    col3.metric("Correct", correct)

    st.markdown("### Final Score")
    st.progress(score_percent / 100)
    st.write(f"### {score_percent}%")

    # -------- Certificate Generator --------
    def generate_certificate(name, score):

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(300, 700, "Certificate of Completion")

        c.setFont("Helvetica", 16)
        c.drawCentredString(300, 650, f"This certifies that")

        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(300, 620, name)

        c.setFont("Helvetica", 16)
        c.drawCentredString(300, 580, "has successfully completed")

        c.drawCentredString(300, 550, "AI Interview Practice")

        c.drawCentredString(300, 510, f"Score: {score}%")

        c.save()

        buffer.seek(0)
        return buffer

    pdf = generate_certificate(st.session_state.username, score_percent)

    st.download_button(
        label="🎓 Download Certificate",
        data=pdf,
        file_name="interview_certificate.pdf",
        mime="application/pdf"
    )

    if st.button("Start Again"):
        st.session_state.page = "home"
        st.session_state.current_q = 0
        st.session_state.scores = []
        st.session_state.start_time = time.time()
        st.rerun() 