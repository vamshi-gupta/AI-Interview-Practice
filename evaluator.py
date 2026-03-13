correct = correct_answers[st.session_state.current_q]

if user_answer == correct:
    score = 10
    st.success("✅ Correct Answer")
else:
    score = 0
    st.error("❌ Incorrect Answer")