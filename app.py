import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Load environment variables from .env file
load_dotenv()

# Configure Generative AI with API key from environment variable
genai.configure(api_key=os.getenv("google_api_key"))

prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video, providing an important summary within 250 words.
Please provide the summary of the text given here: """

# Function to extract transcript details from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        # Extract video ID from the URL using regular expressions
        video_id = re.findall(r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})", youtube_video_url)[0]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        # Concatenate transcript text
        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e

# Function to generate summary using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    
    # Extract detailed notes from the response
    detailed_notes = ""
    for part in response.candidates[0].content.parts:
        detailed_notes += part.text.strip() + "\n\n"

    return detailed_notes

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        # Extract video ID and display thumbnail image
        video_id = re.findall(r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})", youtube_link)[0]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.error("Invalid YouTube video link provided.")

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
