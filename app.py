
import streamlit as st
import pandas as pd
from django.urls import reverse
from django.shortcuts import render
from streamlit_chat import message
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import(
    SystemMessage,
    HumanMessage,
    AIMessage
)

openai_api_key = "Enter your API Key"

if openai_api_key is None or openai_api_key == "":
    print("OPENAI_API_KEY is not set")
    exit(1)
else:
    print("OPENAI_API_KEY is set")

# Load the dataset
dataset_path = 'dataset.xlsx'  
df = pd.read_excel(dataset_path)

st.set_page_config(
        page_title="Policy Recommendation",
        page_icon="🧑‍⚕️"
    )

# Sidebar navigation
menu = ["About", "Policy Recommendation",  "Insurance Risk Assessment", "Chat with Bot"]
choice = st.sidebar.radio("Navigation", menu)

if choice == "Policy Recommendation":
    st.title("Policy Recommendation System")
    # User input section
    all_categories = df['Category'].str.split(', ').explode().unique()
    selected_categories = st.multiselect("Select Age Categories:", all_categories)
    st.text("Child: 0-17 yrs\nAdult: 18-59 yrs\nSenior: 60 yrs and above")

    # Filter the dataset based on selected categories
    filtered_df = df[df['Category'].apply(lambda x: any(cat in selected_categories for cat in x.split(', ')))]

  
    min_monthly_installment_range = st.slider("Approximate Minimum Monthly Installment:", 300, 5000, (300, 5000))
    min_basic_sum_assured_range = st.slider("Minimum Basic Sum Assured:", 50000, 5000000, (50000, 5000000))

    
    filtered_df = filtered_df[
        (filtered_df['Min Monthly Installment Amount'] >= min_monthly_installment_range[0]) &
        (filtered_df['Min Monthly Installment Amount'] <= min_monthly_installment_range[1]) &
        (filtered_df['Min Basic Sum Assured'] >= min_basic_sum_assured_range[0]) &
        (filtered_df['Min Basic Sum Assured'] <= min_basic_sum_assured_range[1])
    ]

    # Display recommendations
    st.subheader("Recommended Policies:")

    if filtered_df.empty:
        st.info("No policies match the selected criteria.")
    else:
        for index, row in filtered_df.iterrows():
            st.write(f"**Policy Name:** {row['Policy']}")
            st.write(f"**Min Age:** {row['Min Age']} - **Max Age:** {row['Max Age']}")
            st.write(f"**Age Category:** {row['Category']}")
            st.write(f"**Min Basic Assured:** {row['Min Basic Sum Assured']}")
            st.write(f"**Max Basic Assured:** {row['Max Basic Sum Assured']}")
            st.write(f"**Policy Term:** {row['Policy Term']}")
            st.write(f"**Min Monthly Installment:** {row['Min Monthly Installment Amount']}")
            st.write(f"**Link for Further Details:** [{row['Link']}]({row['Link']})")
            st.write("---")

elif choice == "About":
    # About page content
    st.title("About Policy Recommendations")
    st.write("""
    This system helps you find suitable health insurance policies based on your preferences.
    
    - Select age categories and additional filters to narrow down policy options.
    - The system recommends policies that match your criteria.
    - Explore details such as policy name, age range, basic sum assured, and more.

    Remember to review the recommendations carefully and consider consulting with insurance professionals for personalized advice.
    """)

    st.subheader("Life Insurance")

    st.write("""
    A life insurance policy is defined as a contract between the insurer and policyholder, wherein the insurer promises to pay a life cover (life assured) to the nominee in exchange for a premium amount, upon the death of the policyholder or after a set time. These plans are the best way to create wealth & secure your family’s future in the event of your unfortunate death. Life insurance can be availed either through “Term plans” that offer life cover for the family’s protection or through “Investment Plans” that help create wealth with financial security to meet an individual's financial goals.
             """)
        
    st.subheader("Key Features & Benefits of Life Insurance Policy")
    st.write("""
    **Financial Security:** The primary benefit of a life insurance policy plans is that it provides long time financial stability to the policyholder’s family in case of any unfortunate event.

    **Death Benefit:** In case of any unfortunate event with the policyholder, the insurer provides financial protection in form of a death payout. The appointed nominee receives the entire sum assured plus the bonus accumulated over a time

    **Maturity Benefits:** When the life insurance policy matures, some life insurance plans offer the policyholder the full premium amount paid during the policy term.
    """)
    
elif choice == "Insurance Risk Assessment":

    # Insurance Risk Assessment page content
    def underwriting():
        st.subheader("Underwriting Information")

        # Gather user information
        age = st.number_input("Enter your age:", min_value=0, max_value=120, step=1)
        health_status = st.selectbox("Select your health status:", ["Excellent", "Good", "Average", "Poor"])
        occupation = st.text_input("Enter your occupation:")

        return {"age": age, "health_status": health_status, "occupation": occupation}

    def risk_identification():
        st.subheader("Risk Identification")

        # Gather risk-related information
        has_health_condition = st.checkbox("Do you have any pre-existing health conditions?")
        has_occupation_risk = st.checkbox("Does your occupation involve high risk?")
        has_property = st.checkbox("Do you want property insurance?")
        has_liability = st.checkbox("Do you want liability insurance?")

        return {
            "has_health_condition": has_health_condition,
            "has_occupation_risk": has_occupation_risk,
            "has_property": has_property,
            "has_liability": has_liability,
        }

    def actuarial_analysis():
        st.subheader("Actuarial Analysis")

        # Gather actuarial information
        projected_claim_amount = st.number_input("Enter the projected claim amount:", min_value=0, step=1000)
        premium_offer = st.number_input("Enter the premium offer:", min_value=0, step=100)

        return {"projected_claim_amount": projected_claim_amount, "premium_offer": premium_offer}

    def insurance_risk_assessment():
        st.title("Insurance Risk Assessment")

        # Gather information for underwriting
        underwriting_info = underwriting()

        # Gather risk-related information
        risk_info = risk_identification()

        # Perform actuarial analysis
        actuarial_info = actuarial_analysis()

        # Display assessment results
        st.subheader("Risk Assessment Results")
        st.write("Based on the information provided, the insurance risk assessment results are as follows:")

        risk_score = calculate_risk_score(underwriting_info, risk_info, actuarial_info)

        st.write(f"Risk Score: {risk_score}")

        user_risk_score = calculate_risk_score(underwriting_info, risk_info, actuarial_info)
        analyze_risk_score(user_risk_score)

    def calculate_risk_score(underwriting_info, risk_info, actuarial_info):
        age_factor = underwriting_info["age"] * 0.1
        health_condition_factor = 1 if risk_info["has_health_condition"] else 0
        occupation_risk_factor = 2 if risk_info["has_occupation_risk"] else 0
        projected_claim_factor = actuarial_info["projected_claim_amount"] * 0.0005

        risk_score = age_factor + health_condition_factor + occupation_risk_factor + projected_claim_factor
        return risk_score
    
    def analyze_risk_score(risk_score):
        st.subheader("Risk Score Analysis")

        # Define risk categories
        low_risk_threshold = 30
        moderate_risk_threshold = 60

        # Display risk score
        st.write(f"Your Risk Score: {risk_score}")

        # Analyze and categorize the risk
        if risk_score < low_risk_threshold:
            st.success("Low Risk")
            st.write("Congratulations! Your risk level is low.")
        elif low_risk_threshold <= risk_score < moderate_risk_threshold:
            st.warning("Moderate Risk")
            st.write("Your risk level is moderate. Consider taking preventive measures and exploring insurance options.")
        else:
            st.error("High Risk")
            st.write("Your risk level is high. It's important to review your insurance coverage and consider risk mitigation strategies.")

        st.subheader("Recommendations and Next Steps")
        st.write("Based on your risk assessment, here are some recommendations:")
        st.write("- Consider consulting with an insurance agent to discuss your coverage options.")
        st.write("- Explore additional coverage for specific risks identified in the assessment.")
        st.write("- Take preventive measures to reduce risk factors, such as adopting a healthier lifestyle.")    

        
    insurance_risk_assessment()

elif choice == "Chat with Bot":

    # chat=ChatOpenAI(temperature=0)
    chat = ChatOpenAI(openai_api_key=openai_api_key,temperature=0)
    
    if "messages" not in st.session_state:

        st.session_state.messages=[
            SystemMessage(content= "You are a helpful assistant. ")
        ]
    
    st.header("Chat with Bot 🤖")
    message("Hello, how may I help you?")

    with st.sidebar:
        user_input=st.text_input("Your message: ", key= "user_input")

    if user_input:
        # message(user_input, is_user=True)
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("Thinking..."):
            response= chat(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))

        # message(response.content, is_user=False)

    messages=st.session_state.get('messages', [])
    for i, msg in enumerate(messages[1:]):
        if i%2==0:
            message(msg.content, is_user=True, key=str(i)+'_user')
        else:
            message(msg.content, is_user=False, key=str(i)+'_ai')

    # st.markdown('<meta http-equiv="refresh" content="0; URL=http://127.0.0.1:8000/streamlit_integration/">', unsafe_allow_html=True)
    # return redirect('streamlit_integration')
    # Redirect to the Django view that integrates Streamlit
    # st.markdown('<meta http-equiv="refresh" content="0; URL=http://127.0.0.1:8000/streamlit_integration/">', unsafe_allow_html=True)
