import streamlit as st
from simpleaichat import AIChat
from typing import Tuple
import os

# Define the options for each dropdown
DRUG = ["Technology", "Science", "History", "Literature", "Arts"]
TONES = ["Formal", "Casual", "Humorous", "Professional", "Empathetic"]
LENGTHS = ["Very Short", "Short", "Medium", "Long", "Very Long"]
PERSPECTIVES = ["Objective", "Subjective", "Critical", "Supportive", "Neutral"]
FORMATS = ["Paragraph", "Bullet Points", "List", "Storytelling", "Dialogue"]

# Initialize AI chat as None, we'll create it after getting the API key
ai = None

def initialize_ai_chat(api_key: str):
    """Initialize the AI chat with the provided API key."""
    global ai
    os.environ['OPENAI_API_KEY'] = api_key
    ai = AIChat(console=False)

def get_user_input() -> Tuple[str, str, str, str, str]:
    """Get user input from five dropdowns."""
    topic = st.selectbox("Select a topic:", DRUG)
    tone = st.selectbox("Select the tone:", TONES)
    length = st.selectbox("Select the content length:", LENGTHS)
    perspective = st.selectbox("Select the perspective:", PERSPECTIVES)
    format = st.selectbox("Select the content format:", FORMATS)
    return topic, tone, length, perspective, format

def generate_prompt(topic: str, tone: str, length: str, perspective: str, format: str) -> str:
    """Generate a prompt for the AI based on user input."""
    return f"""Generate content based on the following criteria:
    1. Topic: {topic}
    2. Tone: Use a {tone.lower()} tone.
    3. Length: Provide a {length.lower()} piece of content. 
       (Very Short: 1-2 sentences, Short: 3-4 sentences, Medium: 1-2 paragraphs, Long: 3-4 paragraphs, Very Long: 5+ paragraphs)
    4. Perspective: Approach the content from a {perspective.lower()} perspective.
    5. Format: Present the content in a {format.lower()} format.

    Create engaging and informative content that strictly adheres to all five criteria."""

def get_ai_response(prompt: str) -> str:
    """Get a response from the AI using simpleaichat."""
    if ai is None:
        raise ValueError("AI chat has not been initialized. Please provide an API key.")
    return ai(prompt)

def main():
    st.title("AI Analog Finder Tool")

    # Check if API key is already in session state
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ''

    # API key input
    api_key = st.text_input("Enter your OpenAI API key:", value=st.session_state.openai_api_key, type="password")
    
    if api_key:
        st.session_state.openai_api_key = api_key
        initialize_ai_chat(api_key)

        topic, tone, length, perspective, format = get_user_input()
        
        if st.button("Generate Content"):
            try:
                with st.spinner("Generating content..."):
                    prompt = generate_prompt(topic, tone, length, perspective, format)
                    content = get_ai_response(prompt)
                    st.write("Generated Content:", content)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter your OpenAI API key")

if __name__ == "__main__":
    main()