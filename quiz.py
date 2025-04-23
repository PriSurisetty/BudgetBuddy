import streamlit as st
import time

def render_quiz():
    """Render the financial profile quiz page"""
    st.title("🏡 Let's Find Your Perfect Home Match")

    with st.form("financial_quiz"):
        st.subheader("🎯 Section 1: Basic Info")

        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("Min Price ($)",
                                        min_value=50000,
                                        value=int(st.session_state.user_data.get('min_price', 300000)),
                                        step=10000)
        with col2:
            max_price = st.number_input("Max Price ($)",
                                        min_value=50000,
                                        value=int(st.session_state.user_data.get('max_price', 500000)),
                                        step=10000)

        # Store the average as the budget
        st.session_state.user_data['budget'] = (min_price + max_price) / 2
        st.session_state.user_data['min_price'] = min_price
        st.session_state.user_data['max_price'] = max_price

        # Location input
        st.session_state.user_data['location'] = st.text_input("Where are you looking to buy? (City, State, or ZIP)",
                                                               value=st.session_state.user_data.get('location', ''))

        st.divider()
        st.subheader("💼 Section 2: Income")

        monthly_income = st.number_input("What is your total monthly income (before taxes)? ($)",
                                         min_value=0,
                                         value=int(st.session_state.user_data.get('monthly_income', 0)),
                                         step=100)

        # Convert monthly to annual for backend compatibility
        st.session_state.user_data['income'] = monthly_income * 12
        st.session_state.user_data['monthly_income'] = monthly_income

        has_cobuyer = st.radio("Do you have a co-buyer?", ["No", "Yes"],
                               index=0 if not st.session_state.user_data.get('has_cobuyer') else 1)

        st.session_state.user_data['has_cobuyer'] = (has_cobuyer == "Yes")

        if has_cobuyer == "Yes":
            cobuyer_income = st.number_input("Co-buyer monthly income ($)",
                                             min_value=0,
                                             value=int(st.session_state.user_data.get('cobuyer_income', 0)),
                                             step=100)
            st.session_state.user_data['cobuyer_income'] = cobuyer_income
            st.session_state.user_data['income'] += (cobuyer_income * 12)

        st.divider()
        st.subheader("💳 Section 3: Debt")

        monthly_debt = st.number_input("What are your total monthly debt payments? ($)",
                                       min_value=0,
                                       value=int(st.session_state.user_data.get('loans', 0)),
                                       step=50,
                                       help="Include credit cards, student loans, car loans, etc.")

        st.session_state.user_data['loans'] = monthly_debt

        has_outstanding_loans = st.radio("Do you currently have any outstanding loans?",
                                         ["No", "Yes"],
                                         index=0 if not st.session_state.user_data.get('has_outstanding_loans') else 1)

        st.session_state.user_data['has_outstanding_loans'] = (has_outstanding_loans == "Yes")

        if has_outstanding_loans == "Yes":
            col1, col2, col3 = st.columns(3)
            with col1:
                loan_type = st.selectbox("Type of loan",
                                         ["Mortgage", "Auto Loan", "Student Loan", "Personal Loan", "Other"],
                                         index=0)
            with col2:
                loan_balance = st.number_input("Balance ($)",
                                               min_value=0,
                                               value=int(st.session_state.user_data.get('loan_balance', 0)),
                                               step=1000)
            with col3:
                loan_payment = st.number_input("Monthly Payment ($)",
                                               min_value=0,
                                               value=int(st.session_state.user_data.get('loan_payment', 0)),
                                               step=50)

            st.session_state.user_data['loan_type'] = loan_type
            st.session_state.user_data['loan_balance'] = loan_balance
            st.session_state.user_data['loan_payment'] = loan_payment

        credit_score_options = ["Below 580 (Poor)", "580–669 (Fair)", "670–739 (Good)",
                                "740–799 (Very Good)", "800+ (Excellent)"]

        credit_score_selection = st.selectbox("What's your current credit score?",
                                              credit_score_options,
                                              index=2)  # Default to "Good"

        # Map the credit score range to a numeric value for calculations
        credit_score_mapping = {
            "Below 580 (Poor)": 550,
            "580–669 (Fair)": 625,
            "670–739 (Good)": 700,
            "740–799 (Very Good)": 770,
            "800+ (Excellent)": 810
        }

        st.session_state.user_data['credit_score'] = credit_score_mapping[credit_score_selection]
        st.session_state.user_data['credit_range'] = credit_score_selection

        st.divider()
        st.subheader("📊 Section 4: Financial Health")

        down_payment = st.number_input("How much do you have saved for a down payment? ($)",
                                       min_value=0,
                                       value=int(st.session_state.user_data.get('savings', 0)),
                                       step=1000)

        st.session_state.user_data['savings'] = down_payment

        include_closing_costs = st.radio("Do you want to include estimated closing costs in your budget?",
                                         ["Yes", "No", "Not sure"],
                                         index=0 if st.session_state.user_data.get('include_closing_costs', True) else
                                         (1 if st.session_state.user_data.get('include_closing_costs') is False else 2))

        st.session_state.user_data['include_closing_costs'] = (include_closing_costs == "Yes")

        know_dti = st.radio("Do you know your Debt-to-Income (DTI) ratio?",
                            ["Yes, I know it", "No, please calculate it for me"],
                            index=0 if st.session_state.user_data.get('knows_dti', False) else 1)

        st.session_state.user_data['knows_dti'] = (know_dti == "Yes, I know it")

        if know_dti == "Yes, I know it":
            dti_ratio = st.number_input("Enter your DTI ratio (%)",
                                        min_value=0.0,
                                        max_value=100.0,
                                        value=float(st.session_state.user_data.get('dti_ratio', 0.0)),
                                        step=0.1)
            st.session_state.user_data['dti_ratio'] = dti_ratio
        else:
            # Calculate DTI if user doesn't know it
            if monthly_income > 0:
                dti = (monthly_debt / monthly_income) * 100
                st.session_state.user_data['dti_ratio'] = round(dti, 2)
                st.metric("Your calculated DTI ratio", f"{st.session_state.user_data['dti_ratio']}%")

        st.divider()
        st.subheader("🏠 Section 5: Home Goals")

        timeline_options = ["Within 3 months", "3–6 months", "6–12 months", "Just browsing"]
        timeline = st.radio("When are you planning to buy?",
                            timeline_options,
                            index=timeline_options.index(st.session_state.user_data.get('timeline', "Just browsing"))
                            if st.session_state.user_data.get('timeline') in timeline_options else 3)

        st.session_state.user_data['timeline'] = timeline

        home_type_options = ["Single-family", "Condo/Townhome", "Multi-family", "Not sure"]
        home_type = st.selectbox("What type of home are you looking for?",
                                 home_type_options,
                                 index=home_type_options.index(st.session_state.user_data.get('home_type', "Not sure"))
                                 if st.session_state.user_data.get('home_type') in home_type_options else 3)

        st.session_state.user_data['home_type'] = home_type

        usage_options = ["Live in it", "Rent it", "Both"]
        usage = st.radio("Do you plan to live in the home or rent it out?",
                         usage_options,
                         index=usage_options.index(st.session_state.user_data.get('usage', "Live in it"))
                         if st.session_state.user_data.get('usage') in usage_options else 0)

        st.session_state.user_data['usage'] = usage

        # Name field at the end for optional identification
        st.session_state.user_data['name'] = st.text_input("Your Name (Optional)",
                                                           value=st.session_state.user_data.get('name', ''))

        # Calculate monthly expenses to maintain compatibility with original code
        # This is just a placeholder - in a real app you might calculate this differently
        st.session_state.user_data['monthly_expenses'] = monthly_debt

        submit = st.form_submit_button("Find My Perfect Home Match")

        if submit:
            with st.spinner("Bud is crunching the numbers..."):
                # Simulate a brief delay for effect
                time.sleep(1)

            st.success("Your financial profile has been updated successfully!")

            # Calculate affordability
            if st.session_state.user_data['income'] > 0:
                affordable_amount = st.session_state.user_data['income'] * 4
                if st.session_state.user_data['budget'] > affordable_amount * 1.2:
                    st.warning(
                        f"Your budget may be high relative to your income. A recommended budget based on your income would be around ${affordable_amount:,.2f}")

            st.session_state.page = "Budgeting"