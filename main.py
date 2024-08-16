import streamlit as st
from openai import OpenAI
from typing import Tuple
import os

# Define the options for the remaining dropdowns
AVAIL = ["Are approved therapies only","Include therapies still in clinical trial"]

# Initialize OpenAI client as None, we'll create it after getting the API key
client = None

def initialize_openai_client(api_key: str):
    """Initialize the OpenAI client with the provided API key."""
    global client
    client = OpenAI(api_key=api_key)

def get_user_input() -> Tuple[str, str]:
    """Get user input from two text fields and three dropdowns."""
    a = st.text_input("Enter therapeutic area")
    b = st.selectbox("Select commercialization status:", AVAIL)
    return a, b

def generate_response(a: str, b: str) -> str:
    """Generate a response using GPT-4 with its built-in search capability."""
    if client is None:
        raise ValueError("OpenAI client has not been initialized. Please provide an API key.")

    prompt = f"""
You are an AI assistant acting as a market access expert for a large pharmaceutical company. Your task is to propose a list of up to 10 top competitors or analogs (not developed by Sanofi) in the specified therapeutic area. Provide detailed information and justifications for your proposals.
Input Parameters:

Therapeutic Area: {a}
Commercialization Status: {b}

Selection Criteria:

The proposed analogs must be drugs that {b}.
Relevance to the specified therapeutic area: {a}
Market impact and potential
Innovative features or mechanisms of action
Competitive positioning in the market
Disease prevalence

For each proposed analog, provide the following information:

Drug Name: [Name of the analog]
Manufacturer: [Pharmaceutical company producing the drug]
Treatment Disease and Indication(s): [Specific conditions the drug treats]
Market Approval:

Number of major markets that have approved the analog: [X markets]
Names of these markets: [List major markets]
FDA/EMA Status: [Approval status and date, if available]


Target Population:

Estimated size: [X patients]
If exact number unavailable: [Estimated prevalence as "X patients per XXX inhabitants"]


Clinical Studies:

List of key clinical studies: [Study names/acronyms, separated by semicolons]


Disease Burden and Mortality:

Quantitative data on disease burden: [Include statistics if available]
Mortality rates or impact: [Include data if available]


Reimbursement Status (as of [current year]):

United States: [Status and year approved]
France: [Status and year approved]
Italy: [Status and year approved]
United Kingdom: [Status and year approved]
Spain: [Status and year approved]
Germany: [Status and year approved]


Key Differentiators:

Briefly explain what makes this analog stand out in the market


Justification:

Provide a concise explanation of why this analog was selected, considering the criteria mentioned above



Additional Instructions:

Ensure all information is up-to-date and accurate.
If specific data points are not available, clearly state so and provide the best available alternative information.
Present the information in a clear, structured format for easy readability.
Limit your response to the top 10 most relevant analogs, even if more are available.
If fewer than 10 relevant analogs exist, provide information on all that meet the criteria.

Please proceed with your analysis and present the findings based on these guidelines.
    """

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant with the ability to browse the internet for up-to-date information."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",  # This model has browsing capabilities
        messages=messages,
        max_tokens=4000,  # Adjust based on your needs
        temperature=0.6
    )

    return response.choices[0].message.content

def main():
    st.title("AI Analog Initial Assessment")

    # Check if API key is already in session state
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ''

    # API key input
    api_key = st.text_input("Enter your OpenAI API key:", value=st.session_state.openai_api_key, type="password")
    
    if api_key:
        st.session_state.openai_api_key = api_key
        initialize_openai_client(api_key)

        drug, length = get_user_input()
        
        if st.button("Generate"):
            if drug:  # Ensure that drug and length are not empty
                try:
                    with st.spinner("Searching and generating content..."):
                        content = generate_response(drug, length)
                        st.write("Generated Content:", content)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please enter a drug name and select a length.")
    else:
        st.warning("Please enter your OpenAI API key")

if __name__ == "__main__":
    main()
