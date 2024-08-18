import streamlit as st
from openai import OpenAI
from typing import Tuple
import markdown2
from xhtml2pdf import pisa
from io import BytesIO

# Initialize OpenAI client as None, we'll create it after getting the API key
client = None

def initialize_openai_client(api_key: str):
    """Initialize the OpenAI client with the provided API key."""
    global client
    client = OpenAI(api_key=api_key)

def get_user_input() -> Tuple[str, str]:
    """Get user input from two text fields."""
    a = st.text_input("Enter API Name")
    b = st.text_input("Enter Country Name")
    return a, b

def generate_response(api_name: str, country: str) -> str:
    """Generate a response using GPT-4 with a focus on patent information."""
    if client is None:
        raise ValueError("OpenAI client has not been initialized. Please provide an API key.")

    prompt = f"""
Provide a comprehensive analysis of all available patent information for the drug {api_name} in {country}. Include as much of the following information as possible.
Present the information in a clear, structured format using Markdown. Use appropriate Markdown syntax for headings, lists, and emphasis. Provide as much detail as possible based on the information available to you.
"""

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant with knowledge about pharmaceutical patents. Format your response using Markdown."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=3000,
        temperature=0.6
    )

    return response.choices[0].message.content

def create_pdf(content: str) -> BytesIO:
    """Create a PDF from the generated markdown content."""
    # Convert markdown to HTML
    html = markdown2.markdown(content)
    
    # Wrap the HTML content in a basic HTML structure with some CSS for better formatting
    full_html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
    </head>
    <body>
    {html}
    </body>
    </html>
    """
    
    # Create a PDF from the HTML
    pdf_buffer = BytesIO()
    pisa.CreatePDF(full_html, dest=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def main():
    st.title("Pharmaceutical Patent Analysis Tool")

    # Check if API key is already in session state
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ''

    # API key input
    api_key = st.text_input("Enter your OpenAI API key:", value=st.session_state.openai_api_key, type="password")
    
    if api_key:
        st.session_state.openai_api_key = api_key
        initialize_openai_client(api_key)

        api_name, country = get_user_input()
        
        if st.button("Generate"):
            if api_name and country:  # Ensure that both inputs are not empty
                try:
                    with st.spinner("Generating patent analysis..."):
                        content = generate_response(api_name, country)
                        st.markdown(content)  # Display content as markdown
                        
                        # Create PDF
                        pdf_buffer = create_pdf(content)
                        
                        # Provide download button for PDF
                        st.download_button(
                            label="Download PDF",
                            data=pdf_buffer,
                            file_name=f"patent_analysis_{api_name}_{country}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please enter both API Name and Country Name.")
    else:
        st.warning("Please enter your OpenAI API key")

if __name__ == "__main__":
    main()
