import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def calculate_mortgage_payment(principal, annual_interest_rate, term_years):
    """Calculate monthly mortgage payment"""
    monthly_interest_rate = annual_interest_rate / 12 / 100
    num_payments = term_years * 12
    if monthly_interest_rate == 0:
        return principal / num_payments
    monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / (
            (1 + monthly_interest_rate) ** num_payments - 1)
    return monthly_payment


def generate_amortization_schedule(principal, annual_interest_rate, term_years, start_date):
    """Generate amortization schedule for loan"""
    monthly_payment = calculate_mortgage_payment(principal, annual_interest_rate, term_years)
    schedule = []

    remaining_balance = principal
    monthly_interest_rate = annual_interest_rate / 12 / 100

    payment_date = datetime.strptime(start_date, "%Y-%m-%d")

    for i in range(term_years * 12):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment

        schedule.append({
            "payment_number": i + 1,
            "date": payment_date.strftime("%Y-%m-%d"),
            "payment": monthly_payment,
            "principal": principal_payment,
            "interest": interest_payment,
            "remaining_balance": max(0, remaining_balance)
        })

        payment_date = payment_date + timedelta(days=30)

    return schedule


def render_loan_tracker():
    """Render the loan tracker page"""
    st.title("Mortgage & Loan Tracker")

    if 'loan_info' not in st.session_state:
        st.session_state.loan_info = {
            'principal': 0,
            'interest_rate': 0,
            'term_years': 30,
            'start_date': datetime.now().strftime("%Y-%m-%d")
        }

    if not st.session_state.loan_info['principal']:
        st.info("No loan information yet. Either search for a property first or enter loan details manually.")

    with st.form("loan_info_form"):
        st.subheader("Loan Details")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.loan_info['principal'] = st.number_input(
                "Loan Amount ($)",
                min_value=0.0,
                value=float(st.session_state.loan_info['principal']),
                step=10000.0
            )

            st.session_state.loan_info['interest_rate'] = st.number_input(
                "Interest Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=float(st.session_state.loan_info['interest_rate'] or 6.5),
                step=0.1
            )

        with col2:
            st.session_state.loan_info['term_years'] = st.selectbox(
                "Loan Term (years)",
                options=[15, 20, 30],
                index=2 if st.session_state.loan_info['term_years'] == 30 else (
                    1 if st.session_state.loan_info['term_years'] == 20 else 0)
            )

            st.session_state.loan_info['start_date'] = st.date_input(
                "Loan Start Date",
                value=datetime.strptime(st.session_state.loan_info['start_date'], "%Y-%m-%d") if
                st.session_state.loan_info['start_date'] else datetime.now()
            ).strftime("%Y-%m-%d")

        if st.form_submit_button("Calculate Payment"):
            st.session_state.show_amortization = True

    if st.session_state.loan_info['principal'] > 0 and getattr(st.session_state, 'show_amortization', False):
        monthly_payment = calculate_mortgage_payment(
            st.session_state.loan_info['principal'],
            st.session_state.loan_info['interest_rate'],
            st.session_state.loan_info['term_years']
        )

        total_interest = (monthly_payment * 12 * st.session_state.loan_info['term_years']) - st.session_state.loan_info[
            'principal']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Monthly Payment", f"${monthly_payment:,.2f}")

        with col2:
            st.metric("Total Interest", f"${total_interest:,.2f}")

        with col3:
            total_cost = st.session_state.loan_info['principal'] + total_interest
            st.metric("Total Cost", f"${total_cost:,.2f}")

        st.subheader("Amortization Schedule")

        tab1, tab2 = st.tabs(["Overview", "Full Schedule"])

        with tab1:
            # Create amortization schedule
            schedule = generate_amortization_schedule(
                st.session_state.loan_info['principal'],
                st.session_state.loan_info['interest_rate'],
                st.session_state.loan_info['term_years'],
                st.session_state.loan_info['start_date']
            )

            # Prepare data for visualization
            years = [1, 5, 10, 15, 20, 30]
            years = [y for y in years if y <= st.session_state.loan_info['term_years']]

            # Extract data points for visualization
            balance_data = []
            principal_paid_data = []
            interest_paid_data = []

            initial_principal = st.session_state.loan_info['principal']

            for year in years:
                payment_index = year * 12 - 1
                if payment_index < len(schedule):
                    payment = schedule[payment_index]
                    balance_data.append(payment['remaining_balance'])

                    # Calculate cumulative principal and interest paid
                    principal_paid = initial_principal - payment['remaining_balance']
                    principal_paid_data.append(principal_paid)

                    interest_paid = payment['payment_number'] * monthly_payment - principal_paid
                    interest_paid_data.append(interest_paid)

            # Create a line chart showing remaining balance over time
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(years, balance_data, marker='o', linestyle='-', color='blue', label='Remaining Balance')
            ax.set_xlabel('Years')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Mortgage Balance Over Time')
            ax.grid(True)

            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

            st.pyplot(fig)

            # Create a stacked bar chart showing principal vs interest
            fig, ax = plt.subplots(figsize=(10, 6))
            width = 0.5

            ax.bar(years, principal_paid_data, width, label='Principal Paid', color='green')
            ax.bar(years, interest_paid_data, width, bottom=principal_paid_data, label='Interest Paid', color='red')

            ax.set_xlabel('Years')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Principal vs. Interest Paid Over Time')
            ax.legend()

            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

            st.pyplot(fig)

        with tab2:
            # Display full amortization schedule
            schedule = generate_amortization_schedule(
                st.session_state.loan_info['principal'],
                st.session_state.loan_info['interest_rate'],
                st.session_state.loan_info['term_years'],
                st.session_state.loan_info['start_date']
            )

            # Create a DataFrame for display
            df = pd.DataFrame(schedule)
            # Format the columns for better display
            df['payment'] = df['payment'].map('${:,.2f}'.format)
            df['principal'] = df['principal'].map('${:,.2f}'.format)
            df['interest'] = df['interest'].map('${:,.2f}'.format)
            df['remaining_balance'] = df['remaining_balance'].map('${:,.2f}'.format)

            # Display in chunks of years to avoid overwhelming the UI
            years_to_show = st.slider("Select years to display:", 1, st.session_state.loan_info['term_years'], 5)
            payments_to_show = years_to_show * 12

            st.dataframe(df.head(payments_to_show), hide_index=True)

            # Option to download full schedule as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Full Amortization Schedule",
                data=csv,
                file_name="amortization_schedule.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    render_loan_tracker()