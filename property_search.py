import streamlit as st
import requests
import matplotlib.pyplot as plt


def geocode_address(address):
    """Convert address to latitude and longitude using Nominatim (OpenStreetMap)"""
    # Using Nominatim API which is free but has usage limits
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "PropertySearchApp/1.0"  # Nominatim requires a User-Agent
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])
    else:
        return None, None


def real_property_search(latitude, longitude, radius):
    """Search for properties based on coordinates"""
    url = 'https://realtor16.p.rapidapi.com/search/forsale/coordinates'

    # Query string parameters
    querystring = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
        "limit": 15
    }

    # Headers
    headers = {
        "X-RapidAPI-Key": '15b72aac79mshd0bb48c7bf3d204p166ebcjsn1887614523e1',
        "X-RapidAPI-Host": "realtor16.p.rapidapi.com"
    }

    # Send GET request to API
    response = requests.get(url, headers=headers, params=querystring)

    # Check if response was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        st.error(response.text)
        return None


def render_property_search():
    """Render the property search page"""
    st.title("Property Search")

    # Location input
    location = st.text_input("Enter Location (e.g., 'Houston, TX' or '123 Main St, New York, NY')")

    # Search radius input
    radius = st.number_input("Search Radius (km)", min_value=1, value=30)

    # Advanced Options
    with st.expander("Advanced Options"):
        st.info("If location search doesn't work, you can manually enter coordinates")
        manual_coords = st.checkbox("Enter coordinates manually")

        if manual_coords:
            latitude = st.number_input("Enter Latitude", value=29.27052)
            longitude = st.number_input("Enter Longitude", value=-95.74991)

    if st.button("Search"):
        with st.spinner("Searching for properties..."):
            # Determine coordinates
            if manual_coords:
                lat, lng = latitude, longitude
            else:
                if not location:
                    st.error("Please enter a location")
                    return

                lat, lng = geocode_address(location)
                if lat is None or lng is None:
                    st.error("Could not find coordinates. Try another location or use manual entry.")
                    return

            # Perform search
            properties = real_property_search(lat, lng, radius)

            if properties and "properties" in properties:
                st.subheader(f"Found {len(properties['properties'])} properties")
                st.write("---")
                cols = st.columns(3)

                for i, prop in enumerate(properties.get("properties", [])):
                    with cols[i % 3]:
                        with st.container():
                            # Address
                            if "address" in prop:
                                st.subheader(f"{prop['address']}")
                            elif "location" in prop and "address" in prop["location"]:
                                addr = prop["location"]["address"]
                                st.subheader(f"{addr['line']} {addr.get('city', '')}, {addr.get('state_code', '')}")
                            else:
                                st.subheader("Address not available")

                            # Image
                            img_url = None
                            if "primary_photo" in prop and "href" in prop["primary_photo"]:
                                img_url = prop["primary_photo"]["href"]
                            elif "photos" in prop and prop["photos"] and "href" in prop["photos"][0]:
                                img_url = prop["photos"][0]["href"]

                            if img_url:
                                st.image(img_url, use_container_width=True)
                            else:
                                st.markdown("📷 *No image available*")

                            # Basic Info
                            col1, col2 = st.columns(2)

                            # Get property price
                            list_price = prop.get('list_price', 0)
                            if isinstance(list_price, str) and list_price.isdigit():
                                list_price = int(list_price)

                            with col1:
                                st.markdown(f"**Price:** ${list_price:,}")
                            beds = "N/A"
                            baths = "N/A"
                            if "description" in prop:
                                beds = prop["description"].get("beds", "N/A")
                                baths = prop["description"].get("baths_consolidated",
                                                                prop["description"].get("baths", "N/A"))
                            elif "beds" in prop:
                                beds = prop["beds"]
                            if "baths" in prop:
                                baths = prop["baths"]
                            with col2:
                                st.markdown(f"**Beds/Baths:** {beds}/{baths}")

                            sqft = "N/A"
                            if "description" in prop and "sqft" in prop["description"]:
                                sqft = prop["description"]["sqft"]
                            elif "building_size" in prop:
                                sqft = prop.get("building_size", {}).get("size", "N/A")
                            st.markdown(f"**Area:** {sqft} sqft")

                            # Risk Analysis
                            with st.expander("View Risk Analysis", expanded=False):
                                st.markdown("### Buyer Risk Analysis")

                                # Get user data from session state
                                min_price = st.session_state.user_data.get('min_price', 0)
                                max_price = st.session_state.user_data.get('max_price', 0)
                                credit_score = st.session_state.user_data.get('credit_score', 0)
                                dti_ratio = st.session_state.user_data.get('dti_ratio', 0)
                                savings = st.session_state.user_data.get('savings', 0)

                                # Calculate risk factors

                                # 1. Price Range Risk
                                price_risk = "low"
                                if list_price > max_price:
                                    price_risk = "high"
                                elif list_price > (max_price * 0.9):
                                    price_risk = "moderate"

                                # 2. Credit Score Risk
                                credit_risk = "high"
                                if credit_score >= 740:
                                    credit_risk = "low"
                                elif credit_score >= 660:
                                    credit_risk = "moderate"

                                # 3. DTI Risk
                                dti_risk = "high"
                                if dti_ratio < 36:
                                    dti_risk = "low"
                                elif dti_ratio <= 45:
                                    dti_risk = "moderate"

                                # 4. Down Payment Risk
                                down_payment_percentage = 0
                                if list_price > 0:
                                    down_payment_percentage = (savings / list_price) * 100

                                down_payment_risk = "high"
                                if down_payment_percentage >= 20:
                                    down_payment_risk = "low"
                                elif down_payment_percentage >= 5:
                                    down_payment_risk = "moderate"

                                # Calculate overall risk level
                                risk_scores = {"low": 1, "moderate": 2, "high": 3}
                                avg_risk_score = (risk_scores[price_risk] +
                                                  risk_scores[credit_risk] +
                                                  risk_scores[dti_risk] +
                                                  risk_scores[down_payment_risk]) / 4

                                overall_risk = "high"
                                if avg_risk_score <= 1.5:
                                    overall_risk = "low"
                                elif avg_risk_score <= 2.5:
                                    overall_risk = "moderate"

                                # Display risk analysis
                                risk_color = {
                                    "low": "green",
                                    "moderate": "orange",
                                    "high": "red"
                                }

                                st.markdown(
                                    f"### Overall Risk: <span style='color:{risk_color[overall_risk]};'>{overall_risk.upper()}</span>",
                                    unsafe_allow_html=True)

                                # Show risk breakdown
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("#### Risk Factors:")
                                    st.markdown(
                                        f"- **Price Range**: <span style='color:{risk_color[price_risk]};'>{price_risk}</span>",
                                        unsafe_allow_html=True)
                                    st.markdown(
                                        f"- **Credit Score**: <span style='color:{risk_color[credit_risk]};'>{credit_risk}</span>",
                                        unsafe_allow_html=True)

                                with col2:
                                    st.markdown("&nbsp;")
                                    st.markdown(
                                        f"- **DTI Ratio**: <span style='color:{risk_color[dti_risk]};'>{dti_risk}</span>",
                                        unsafe_allow_html=True)
                                    st.markdown(
                                        f"- **Down Payment**: <span style='color:{risk_color[down_payment_risk]};'>{down_payment_risk}</span>",
                                        unsafe_allow_html=True)

                                # Display risk description based on overall risk
                                st.markdown("### What This Means")

                                if overall_risk == "low":
                                    st.markdown("""
                                    You're a **low-risk buyer** with a strong financial foundation. This includes a high credit score (usually 740+), 
                                    a stable income history, a low debt-to-income (DTI) ratio (below 36%), and the ability to put down a sizable 
                                    down payment (20% or more). As a low-risk buyer, you're attractive to lenders because you've demonstrated 
                                    financial responsibility and have the resources to weather potential market fluctuations or unexpected costs.
                                    """)
                                    st.success("This property appears to be a good match for your financial profile!")

                                elif overall_risk == "moderate":
                                    st.markdown("""
                                    You're a **moderate-risk buyer** with some solid financial indicators but also a few red flags. 
                                    For instance, you may have a decent credit score (around 660–739), a moderate DTI ratio (36–45%), 
                                    or a smaller down payment (5–19%). While you may qualify for a mortgage, you might not get the most 
                                    favorable interest rates or loan terms. Lenders may also require private mortgage insurance (PMI) 
                                    if the down payment is under 20%, adding to the monthly cost.
                                    """)
                                    st.warning(
                                        "You might face some challenges with financing this property. Consider improving your financial situation before proceeding.")

                                else:  # high risk
                                    st.markdown("""
                                    You're a **high-risk buyer** typically with a lower credit score (under 660), inconsistent income, 
                                    a high DTI ratio (above 45%), and minimal savings for a down payment. As a high-risk buyer, you may 
                                    struggle to qualify for traditional loans or may only qualify for high-interest options. In addition, 
                                    you are more vulnerable to financial shocks, such as job loss or unexpected repairs, which increases 
                                    the risk for both you and the lender.
                                    """)
                                    st.error(
                                        "This property may be difficult to finance with your current financial profile. Consider improving your credit score, reducing debt, or increasing your savings before proceeding.")

                                # Show recommendations based on risk factors
                                st.markdown("### Recommendations")

                                recommendations = []

                                if price_risk != "low":
                                    recommendations.append(
                                        "Consider properties within your budget range to avoid overextending financially.")

                                if credit_risk != "low":
                                    recommendations.append(
                                        "Work on improving your credit score to qualify for better interest rates.")

                                if dti_risk != "low":
                                    recommendations.append("Reduce existing debt to improve your debt-to-income ratio.")

                                if down_payment_risk != "low":
                                    recommendations.append(
                                        "Continue saving for a larger down payment to avoid PMI and reduce your loan amount.")

                                if not recommendations:
                                    st.success("You're in great financial shape for this property!")
                                else:
                                    for rec in recommendations:
                                        st.markdown(f"- {rec}")
            else:
                st.error("No properties found or failed to fetch data.")


if __name__ == "__main__":
    render_property_search()