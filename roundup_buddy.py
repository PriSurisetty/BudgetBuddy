import streamlit as st
import requests
import time

def get_customer_data(customer_id, api_key):
    """Convert address to latitude and longitude using Nominatim (OpenStreetMap)"""
    url = f"http://api.nessieisreal.com/customers/{customer_id}?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return customer data
    else:
        return None

def get_accounts_for_customer(customer_id, api_key):
    """Get accounts for a customer"""
    url = f"http://api.nessieisreal.com/customers/{customer_id}/accounts?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return account data
    else:
        return None

def get_purchases_for_account(checking_account_id, api_key):
    """Get purchases for a checking account"""
    url = f"http://api.nessieisreal.com/accounts/{checking_account_id}/purchases?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return purchase data
    else:
        return None

def update_account_balance(account_id, new_balance, api_key):
    """Update account balance"""
    url = f"http://api.nessieisreal.com/accounts/{account_id}?key={api_key}"
    data = {"balance": new_balance}
    response = requests.put(url, json=data)
    st.write(f"Updating account {account_id} with new balance: {new_balance}")
    st.write(f"Response status code: {response.status_code}")
    st.write(f"Response text: {response.text}")
    if response.status_code == 200:
        return response.json()  # Return updated account data
    else:
        return None

def deposit_to_savings(account_id, amount, api_key):
    """Function to create a deposit into savings account"""
    url = f"http://api.nessieisreal.com/accounts/{account_id}/deposits?key={api_key}"
    payload = {
        "medium": "balance",
        "transaction_date": "2025-04-06",  # You can adjust this to the current date if needed
        "amount": amount,
        "description": "Round-up transfer"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        return response.json()
    else:
        print("Deposit failed:", response.status_code, response.text)
        return None

def transfer_to_savings(savings_account_id, checking_account_id, customer_id, api_key):
    """Transfer money from checking to savings"""
    # Fetch purchases from the checking account
    purchases = get_purchases_for_account(checking_account_id, api_key)
    if purchases:
        total_transfer = 0
        for purchase in purchases:
            amount = purchase['amount']
            rounded_up = (int(amount) + 1) if amount != int(amount) else int(amount)
            transfer_amount = round(rounded_up - amount, 2)
            if transfer_amount > 0:
                total_transfer += transfer_amount

        total_transfer = round(total_transfer, 2)

        # Perform deposit via POST (this updates the balance)
        deposit_result = deposit_to_savings(savings_account_id, total_transfer, api_key)
        if deposit_result:
            # Wait for a brief moment to allow the API to reflect the updated balance
            time.sleep(2)  # Wait 2 seconds for the balance to update
            # Re-fetch the actual updated savings account balance
            accounts_data = get_accounts_for_customer(customer_id, api_key)
            if accounts_data:
                updated_savings = next((acct for acct in accounts_data if acct['_id'] == savings_account_id), None)
                if updated_savings:
                    return total_transfer, updated_savings['balance']
        return None
    return None

def authenticate_user(username, password):
    """Dummy authentication function using if/elif statements"""
    if username == "emilyC" and password == "123":
        return "67f1e8999683f20dd5194b84"
    elif username == "avaW" and password == "abc":
        return "67f1e8d59683f20dd5194b85"
    elif username == "ethanM" and password == "456":
        return "67f1e8e19683f20dd5194b86"
    elif username == "sophiaJ" and password == "efg":
        return "67f1e8f19683f20dd5194b87"
    else:
        return None

def display_customer_info(customer_id, api_key):
    """Function to display customer info and purchases"""
    customer_data = get_customer_data(customer_id, api_key)
    if customer_data:
        st.write(f"Customer Name: {customer_data['first_name']} {customer_data['last_name']}")
        st.write(f"Address: {customer_data['address']['street_number']} {customer_data['address']['street_name']}")
        st.write(
            f"City: {customer_data['address']['city']}, {customer_data['address']['state']} {customer_data['address']['zip']}")

        accounts_data = get_accounts_for_customer(customer_id, api_key)
        if accounts_data:
            checking_account_id = None
            savings_account_id = None
            for account in accounts_data:
                if account['type'] == 'Checking':
                    checking_account_id = account['_id']
                if account['type'] == 'Savings':
                    savings_account_id = account['_id']

            if checking_account_id:
                checking_account_data = get_purchases_for_account(checking_account_id, api_key)
                if checking_account_data:
                    st.write("Purchases:")
                    for purchase in checking_account_data:
                        st.write(f" - {purchase['description']}: ${purchase['amount']}")

            if checking_account_id and savings_account_id:
                if st.button("Transfer Leftover Cents to Savings"):
                    result = transfer_to_savings(savings_account_id, checking_account_id, customer_id, api_key)
                    if result is not None:
                        transfer_amount, updated_balance = result
                        st.success(f"Transferred ${transfer_amount:.2f} to your savings account!")
                        st.write(f"Your updated savings balance is now: ${updated_balance:.2f}")
                        st.write("Congratulations! You are one step closer to your financial goals.")
                    else:
                        st.error("Error in transferring funds.")
        else:
            st.error("No accounts found for this customer.")
    else:
        st.error("Customer data not found.")

def render_budgeting():
    """Render login and budgeting UI"""
    st.title("RoundUp Buddy")
    st.subheader("Powered by CapitalOne")
    st.write("Please enter your CapitalOne username and password.")

    # Initialize session state variables if not present
    if 'customer_id' not in st.session_state:
        st.session_state.customer_id = None

    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Login"):
        customer_id = authenticate_user(username, password)
        if customer_id:
            st.session_state.customer_id = customer_id  # Store in session state
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")

    # If a customer is logged in, display their info
    if st.session_state.customer_id:
        api_key = "0d0de272b4e17fab344119646ea1862b"
        display_customer_info(st.session_state.customer_id, api_key)