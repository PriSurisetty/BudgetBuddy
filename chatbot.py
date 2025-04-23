import streamlit as st
import streamlit.components.v1 as components
from google import genai
import time

# Initialize Gemini Client with your API key
# In a production app, you should store this in environment variables
client = genai.Client(api_key="AIzaSyCQwWifDeCAkwQkLfauM7p1RDlHSpqB_DQ")


def generate_gemini_response(prompt):
    """
    Function to send a prompt to Gemini API and return the generated response.
    """
    try:
        # Call the Gemini API to generate a response
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # You can adjust this based on the specific model you want to use
            contents=prompt,
        )
        # Return the text content of the response
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def auto_scroll_js():
    """Add JavaScript for auto-scrolling the chat container"""
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


def get_chatbot_response(user_query):
    """
    Legacy rule-based chatbot response function (can be used as fallback)
    """
    query = user_query.lower()

    if "save" in query and "month" in query:
        income = st.session_state.user_data['income']
        budget = st.session_state.user_data['budget']
        recommended_savings = max(income * 0.2, budget * 0.05)
        return f"Based on your income of ${income:,.2f} and target budget of ${budget:,.2f}, I recommend saving about ${recommended_savings:,.2f} per month towards your home purchase."

    elif "down payment" in query:
        budget = st.session_state.user_data['budget']
        recommended_dp = budget * 0.2
        return f"For a home with your budget of ${budget:,.2f}, a standard 20% down payment would be ${recommended_dp:,.2f}. However, there are programs that allow for as little as 3-5% down."

    elif "dti" in query or "debt to income" in query:
        dti = st.session_state.user_data['dti_ratio']
        if dti > 43:
            return f"Your current DTI ratio is {dti}%, which is above the typical maximum of 43% for qualifying for a mortgage. You might want to reduce some debt before proceeding."
        else:
            return f"Your DTI ratio of {dti}% is within acceptable limits for most mortgage lenders. The standard maximum is 43%."

    elif "afford" in query:
        income = st.session_state.user_data['income']
        max_affordability = income * 4
        return f"With your annual income of ${income:,.2f}, a common rule of thumb suggests you could afford a home up to ${max_affordability:,.2f}, but this depends on your debt, credit score, and other factors."

    else:
        return "I'm your budget buddy! Feel free to ask me about budgeting for a home purchase, down payment requirements, mortgage calculations, or any other financial aspects of buying property."


def render_chat_interface():
    """
    Render the chat interface within an expander
    """
    st.markdown("---")
    st.markdown("### Chat with BudgetBuddy:")

    with st.expander("", expanded=True):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # First, create a container and display all existing messages
        chat_container = st.container()
        with chat_container:
            # Display all messages from history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # Then, handle new input *after* displaying history
        if prompt := st.chat_input("Ask about financing, budgeting, or property buying"):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            # Display user message in the container
            with chat_container.chat_message("user"):
                st.write(prompt)

            # Generate response using Gemini
            with st.spinner("BudgetBuddy is coming up with a response..."):
                response = generate_gemini_response(prompt)

            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})

            # Display assistant response in the container
            with chat_container.chat_message("assistant"):
                st.write(response)

            # Add the auto scroll JavaScript after updating the chat
            auto_scroll_js()

            # Force a rerun to update the chat history display
            st.rerun()

        # Add auto-scroll even when just displaying history (helps with initial load)
        if st.session_state.chat_history:
            auto_scroll_js()


def render_sidebar_chatbot_button():
    """
    Add chat button to sidebar
    """
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False

    if st.sidebar.button("Chat with BudgetBuddy", key="sidebar_chat_button_chatbot"):
        st.session_state.show_chat = not st.session_state.get("show_chat", False)

    if st.session_state.show_chat:
        st.sidebar.success("Chat is open at the bottom of the page!")


def check_and_render_chat():
    """
    Check if chat should be rendered and display it
    """
    if st.session_state.get("show_chat", False):
        render_chat_interface()


if __name__ == "__main__":
    # For testing only - in the main app, you'd call check_and_render_chat()
    # and render_sidebar_chatbot_button() from the main app
    st.title("BudgetBuddy Chatbot Test")

    # Initialize session state for testing
    if "user_data" not in st.session_state:
        st.session_state.user_data = {
            'name': 'Test User',
            'budget': 350000,
            'location': 'Austin, TX',
            'income': 100000,
            'loans': 500,
            'credit_score': 750,
            'dti_ratio': 35,
            'savings': 50000,
            'monthly_expenses': 3000
        }

    st.session_state.show_chat = True
    render_chat_interface()