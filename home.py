import streamlit as st
import streamlit.components.v1 as components

def configure_page():
    """Configure the Streamlit page with updated theme"""
    st.set_page_config(
        page_title="BudgetBuddy - Your Property Buying Companion",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    set_custom_theme()

def set_custom_theme():
    """Set custom CSS for the entire app"""
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --mint-green: #D5F5E3;
        --mint-light: #A2E4B8;
        --mint-dark: #82E0AA;
        --lavender: #E8DAEF;
        --light-blue: #D4F1F9;
        --soft-yellow: #FCF3CF;
    }

    .stApp {
        background-color: var(--mint-green);
    }

    /* Card styling */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Headers */
    h1, h2, h3 {
        color: #2E7D32 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--mint-dark);
        color: white;
        border: none;
        border-radius: 5px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #66BB6A;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: var(--mint-light);
    }

    /* Progress bars */
    .stProgress > div > div {
        background-color: var(--mint-light);
    }

     /* Smooth scroll for chat container */
    .chat-container {
        scroll-behavior: smooth;
    }

    </style>
    """, unsafe_allow_html=True)

def auto_scroll_js():
    """Add JavaScript for scrolling chat container"""
    js = """
    <script>
        function scrollToBottom() {
            // Target the chat expander which contains the messages
            const chatExpanders = window.parent.document.querySelectorAll('.stExpander');
            if (chatExpanders.length > 0) {
                // Get the last expander (which should be the chat)
                const chatExpander = chatExpanders[chatExpanders.length - 1];
                if (chatExpander) {
                    // Find the content part of the expander
                    const expanderContent = chatExpander.querySelector('.stExpander-content');
                    if (expanderContent) {
                        // Scroll the content to the bottom
                        expanderContent.scrollTop = expanderContent.scrollHeight;
                    }

                    // Also attempt to scroll any chat messages container that might exist
                    const chatMessages = chatExpander.querySelectorAll('.stChatMessage');
                    const lastMessage = chatMessages[chatMessages.length - 1];
                    if (lastMessage) {
                        lastMessage.scrollIntoView({behavior: 'smooth'});
                    }
                }
            }

            // Fallback: also scroll the entire page
            window.parent.scrollTo(0, document.body.scrollHeight);
        }

        // Set a delay to ensure content is rendered before scrolling
        setTimeout(scrollToBottom, 200);
    </script>
    """
    return components.html(js, height=0)

def render_sidebar():
    """Render the sidebar menu"""
    st.sidebar.markdown("""
    <div style="text-align: center; padding-bottom: 10px;">
        <h1 style="color: #2E7D32;">BudgetBuddy 🏠</h1>
        <p style="color: #388E3C;">Your Property Buying Companion</p>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Home"):
        st.session_state.page = "Home"

    st.sidebar.markdown("---")

    if st.sidebar.button("1. Financial Profile Quiz"):
        st.session_state.page = "Quiz"

    if st.sidebar.button("2. Roundup Buddy"):
        st.session_state.page = "Budgeting"

    if st.sidebar.button("3. Property Search"):
        st.session_state.page = "Property Search"

    if st.sidebar.button("4. Loan Tracker"):
        st.session_state.page = "Loan Tracker"

    st.sidebar.markdown("---")

    # if st.sidebar.button("Chat with BudgetBuddy"):
    #     st.session_state.show_chat = not st.session_state.get("show_chat", False)

    # Display user info if available
    if st.session_state.user_data['name']:
        st.sidebar.markdown(f"""
        <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px;">
            <h3 style="color: #2E7D32; margin-top: 0;">Welcome, {st.session_state.user_data['name']}!</h3>
            <p>Budget: ${st.session_state.user_data['budget']:,.2f}</p>
            <p>Location: {st.session_state.user_data['location']}</p>
        </div>
        """, unsafe_allow_html=True)

def render_home():
    """Render the home page"""
    set_custom_theme()

    st.title("Welcome to BudgetBuddy")
    st.subheader("Your Complete Property Buying Companion")

    col1, col2 = st.columns([1, 1.25])

    with col1:
        st.markdown("""
        ### Start Your Property Buying Journey Today!

        BudgetBuddy helps you manage all financial aspects of buying property:

        1. **Assess your financial readiness** with our comprehensive quiz
        2. **Plan and save** for your down payment with our budgeting tools
        3. **Find the perfect property** within your budget
        4. **Track your mortgage payments** and build equity

        Get started by taking our financial profile quiz!
        """)

        if st.button("Begin Financial Quiz >>"):
            st.session_state.page = "Quiz"

    with col2:
        st.image("https://wallpaperaccess.com/full/3816377.png", caption="Plan your dream home purchase.",
                 use_container_width=True)

        # Show quick stats with updated styling if user has entered data
        if st.session_state.user_data['budget'] > 0:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 15px; border-radius: 8px; border-left: 4px solid #82E0AA;">
            <h3 style="color: #2E7D32; margin-top: 0;">Your Progress</h3>
            </div>
            """, unsafe_allow_html=True)

            # Calculate a mock affordability score
            income = st.session_state.user_data['income']
            loans = st.session_state.user_data['loans']
            budget = st.session_state.user_data['budget']

            affordability_ratio = min(100, max(0, 100 * (income - loans * 0.1) / (budget)))

            st.progress(affordability_ratio / 100, text=f"Affordability: {affordability_ratio:.1f}%")

            savings_progress = sum(st.session_state.roundup_savings.values()) / (budget * 0.2) * 100
            savings_progress = min(100, max(0, savings_progress))

            st.progress(savings_progress / 100, text=f"Savings Goal: {savings_progress:.1f}%")

    # Close the container div
    st.markdown("</div>", unsafe_allow_html=True)

    # Add feature highlights with pastel colors
    st.markdown("<br>", unsafe_allow_html=True)

    # How it works section
    st.markdown("### How it Works:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background-color: #FCF3CF; padding: 15px; border-radius: 10px; height: 150px; text-align: center;">
            <h3 style="color: #2E7D32;">Financial Planning</h3>
            <p>Personalized budget planning based on your income and goals</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background-color: #E8DAEF; padding: 15px; border-radius: 10px; height: 150px; text-align: center;">
            <h3 style="color: #4A235A;">Property Search</h3>
            <p>Find homes that match your budget and preferences</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background-color: #D4F1F9; padding: 15px; border-radius: 10px; height: 150px; text-align: center;">
            <h3 style="color: #1A5276;">Loan Tracking</h3>
            <p>Visualize your mortgage payments and build equity</p>
        </div>
        """, unsafe_allow_html=True)