import streamlit as st
from home import configure_page, render_home, render_sidebar
from quiz import render_quiz
from roundup_buddy import render_budgeting
from property_search import render_property_search
from loan_tracker import render_loan_tracker
from chatbot import check_and_render_chat, render_sidebar_chatbot_button

# Configure page settings
configure_page()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Home"

if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'name': '',
        'budget': 0,
        'location': '',
        'income': 0,
        'loans': 0,
        'credit_score': 0,
        'dti_ratio': 0,
        'savings': 0,
        'monthly_expenses': 0
    }

if 'roundup_savings' not in st.session_state:
    st.session_state.roundup_savings = {}

# Render sidebar
render_sidebar()
render_sidebar_chatbot_button()

# Render the appropriate page based on session state
if st.session_state.page == "Home":
    render_home()
elif st.session_state.page == "Quiz":
    render_quiz()
elif st.session_state.page == "Budgeting":
    render_budgeting()
elif st.session_state.page == "Property Search":
    render_property_search()
elif st.session_state.page == "Loan Tracker":
    render_loan_tracker()

# Check and render chat if enabled
check_and_render_chat()