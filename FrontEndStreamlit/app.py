import streamlit as st
import requests
from main import generate_story

# Set the page title and favicon
st.set_page_config(page_title="Story Spark", page_icon=":books:")

# Set the background color, font, and image
st.markdown(
    """
    <style>
    body {
        font-family: 'Open Sans', sans-serif;
        background-color: #F8F8FF;
        background-image: url('https://images.unsplash.com/photo-1617032316814-4a5b3d7c3e4f');
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set the page header
st.write(
    """
    <div style='text-align:center;padding:2rem;background-color:#F8F8FF;'>
        <h1 style='color:#FF69B4;font-size:6rem;text-shadow: 2px 2px #ADFF2F;'>Story Spark</h1>
        <h3 style='color:#FF69B4;font-size:2rem;text-shadow: 2px 2px #ADFF2F;'>Empowering kids through an Interactive Story Generation Website</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Set the introduction section
st.markdown("## Introduction")
st.write(
    """
    We have developed an innovative story generation website for kids that takes prompts as input and generates engaging stories complete with images. 
    The website aims to foster creativity, imagination, and language skills in children while providing them with entertaining content. 
    This business plan outlines our vision, market analysis, marketing strategies, and financial projections.
    """
)

# Set the story generation section
st.markdown("## Generate your story")

# Set the input fields
input_genre = st.text_input("Genre", value="Science Fiction")
input_type = st.radio("Choose your story type", options=["Short", "Long"], index=0)
input_level = st.selectbox("Choose level of your child", options=["Toddler", "Pre-School", "School-Age", "Adolescent"], index=0)

# Generate the story on button click
if st.button("Generate Story"):
    # Send the input to the backend endpoint
    story_features={
        "movie_genre": input_genre,
        "grade_level": input_level,
        "prompt_length": input_type.lower()
    }
    try:
        output = generate_story(story_features)
        if output:
            st.text("Generated Story:")
            st.write(output)
        else:
            st.error("Error: Empty response received from the backend")
    except Exception as e:
        st.error("Error: Failed to generate story--", e)

# Set the footer
st.markdown(
    """
    ---
    Created by [Vertex Visionaries] | Powered by [FastAPI](https://fastapi.tiangolo.com/) and [Streamlit](https://streamlit.io/)
    """,
    unsafe_allow_html=True
)
