import streamlit as st
from openai import OpenAI
from typing import Tuple
import os

# Define the options for the remaining dropdowns
AVAIL = ["Are approved therapies only", "Include therapies still in clinical trial"]
VIEW_OPTIONS = ["7 analogs with complete information", "Up to 20 analogs with limited information"]

# Initialize OpenAI client as None, we'll create it after getting the API key
client = None

def initialize_openai_client(api_key: str):
    """Initialize the OpenAI client with the provided API key."""
    global client
    client = OpenAI(api_key=api_key)

def get_user_input() -> Tuple[str, str, str, str]:
    """Get user input from two text fields and three dropdowns."""
    a = st.text_input("Enter therapeutic area or drug name")
    b = st.selectbox("Select commercialization status:", AVAIL)
    c = st.text_input("Enter cutoff launch year (show analogs from this year to present)")
    d = st.selectbox("Select view option:", VIEW_OPTIONS)
    return a, b, c, d

def generate_response(a: str, b: str, c: str, d: str) -> str:
    """Generate a response using GPT-4 with its built-in search capability."""
    if client is None:
        raise ValueError("OpenAI client has not been initialized. Please provide an API key.")

    num_analogs = "7" if d == VIEW_OPTIONS[0] else "20"
    detail_level = "detailed" if d == VIEW_OPTIONS[0] else "limited"

    prompt = f"""
You are an AI assistant acting as a market access expert for a large pharmaceutical company. Your task is to propose a list of up to {num_analogs} top competitors or analogs (no repeat of analogs). Provide {detail_level} information and justifications for your proposals.
Input Parameters:

Therapeutic Area or Drug Name: {a}
Commercialization Status: {b}
Cutoff for launch year (i.e. only show analogs starting the year input by user): {c}
View Option: {d}

Selection Criteria:

The proposed analogs must be drugs that {b}.
Relevance to the specified therapeutic area: {a}
Cutoff for launch year: {c}
Market impact and potential
Innovative features or mechanisms of action
Competitive positioning in the market
Disease prevalence

For each proposed analog, provide the following information:

Drug Name: [Brand Name (API Name)]
Manufacturer: [Pharmaceutical company producing the drug]
Treatment Disease and Indication(s): [Specific conditions the drug treats]
Orphan Drug Designation: [Yes / No, or provide countries that have given orphan drug designation and other major markets that didn't]

{"" if d == VIEW_OPTIONS[1] else '''
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


List Price & HTA Assessment Status (as of [current year]) 
For each market, produce information regarding HTA assessment status, and list price (both per patient per year and per vial price) if available. Include the following details for each country:

United States: [List Price (per patient per year and per vial), FDA approval status and date]
France: [List Price (per patient per year and per vial), HAS assessment - ASMR & SMR ratings]
Italy: [List Price (per patient per year and per vial), AIFA assessment - Innovation status and reimbursement decision]
United Kingdom: [List Price (per patient per year and per vial), NICE decision (recommended, optimized, not recommended)]
Spain: [List Price (per patient per year and per vial), Ministry of Health pricing & reimbursement decision]
Germany: [List Price (per patient per year and per vial), G-BA assessment - Added benefit category]
Japan: [List Price (per patient per year and per vial), PMDA approval status, Pricing Premium status if applicable]

For each country, also include:
- Reimbursement status (if approved)
- Any specific restrictions or conditions for use
- Notable price negotiations or agreements, if public
- Citation of sources used for list price information (provide specific URLs or references for each price point)
- Citation of sources used for HTA assessment information (provide specific URLs or references for each assessment)
'''}

Additional Instructions:

Ensure all information is up-to-date and accurate.
If specific data points are not available, clearly state so and provide the best available alternative information.
Present the information in a clear, structured format for easy readability.
Limit your response to the top {num_analogs} most relevant analogs, even if more are available.
If fewer than {num_analogs} relevant analogs exist, provide information on all that meet the criteria.
No summary or introduction is needed. 
For each list price and HTA assessment provided, include a citation or reference to the source of this information. Use reputable sources such as official government websites, drug pricing databases, or published reports.
Format citations as [Source: URL] immediately after the relevant information.

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

        drug, length, yr, view_option = get_user_input()
        
        if st.button("Generate"):
            if drug:  # Ensure that drug and length are not empty
                try:
                    with st.spinner("Searching and generating content..."):
                        content = generate_response(drug, length, yr, view_option)
                        st.write("Generated Content:", content)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please enter a drug name and select a length.")
    else:
        st.warning("Please enter your OpenAI API key")

if __name__ == "__main__":
    main()
