import streamlit as st
from openai import OpenAI
from typing import Tuple
import os

# Define the options for the remaining dropdowns
LENGTHS = ["Very Short", "Short", "Medium", "Long", "Very Long"]

# Initialize OpenAI client as None, we'll create it after getting the API key
client = None

def initialize_openai_client(api_key: str):
    """Initialize the OpenAI client with the provided API key."""
    global client
    client = OpenAI(api_key=api_key)

def get_user_input() -> Tuple[str, str]:
    """Get user input from two text fields and three dropdowns."""
    drug = st.text_input("Enter the drug name or Therapeutic Area:")
    length = st.selectbox("Select the content length:", LENGTHS)
    return drug, length

def generate_response(drug: str, length: str) -> str:
    """Generate a response using GPT-4 with its built-in search capability."""
    if client is None:
        raise ValueError("OpenAI client has not been initialized. Please provide an API key.")

    prompt = f"""You are a market access expert for a large pharmaceutical company. Your objective is to propose a list of up to 15
    competitors or analogs (not developed by Sanofi, the pharmaceutical company) to the drug or therapeutic area: {drug}. Also, provide your justifications and reasoning behind your proposal decision. 
    Your answer length should be {length}.

    For each proposed analog, provide the following information: 
    1. So far, please share the number and the names of the markets that have approved the analog.
    2. What is the estimated size of the target population (i.e. number of patients)? Please answer in the following format: "X patients." No additional words. If not found, you can provide the estimated prevalence as "X patients per XXX inhabitants"
    3. Which clinical studies were assessed for the analog? Please answer the question with the names of the studies (can be acronyms) separated by semicolons.
    """

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant with the ability to browse the internet for up-to-date information."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",  # This model has browsing capabilities
        messages=messages,
        max_tokens=2000,  # Adjust based on your needs
        temperature=0.6
    )

    return response.choices[0].message.content

def main():
    st.title("AI Analog Finder Tool")

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
