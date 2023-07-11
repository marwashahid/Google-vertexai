from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import service_account
from google.cloud import texttospeech
import google.cloud.aiplatform as aiplatform
import vertexai
from vertexai.language_models import TextGenerationModel
from pydub import AudioSegment
import json
import os

# Load the service account JSON file
# Update the path to your own service account JSON file
service_account_path = "service_account.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

# Initialize the FastAPI application
app = FastAPI()

# Configure CORS for the application
origins = ["http://localhost", "http://localhost:8080", "http://localhost:3000"]
origin_regex = r"https://(.*\.)?alexsystems\.ai"
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model
with open("service_account.json") as f:
    service_account_info = json.load(f)

my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info
)

aiplatform.init(credentials=my_credentials)

with open("service_account.json", encoding="utf-8") as f:
    project_json = json.load(f)
    project_id = project_json["project_id"]

vertexai.init(project=project_id, location="us-central1")

model = TextGenerationModel.from_pretrained("text-bison@001")


@app.get("/generate")
async def generate_story(request: Request):
    """
    Endpoint to generate a story based on query parameters.
    """
    # Define the model parameters
    parameters = {
        "temperature": 1,
        "max_output_tokens": 700,
        "top_p": 0.8,
        "top_k": 40
    }

    # Extract inputs from query parameters
    movie_genre = request.query_params.get("movie_genre", "sci-fi")
    grade_level = request.query_params.get("grade_level", "7")
    prompt_length = request.query_params.get("prompt_length", "short")

    prompt = ""

    # Construct prompt based on inputs
    if prompt_length == "short":
        prompt = f"Generate an imaginative {movie_genre} story suitable for {grade_level} graders in under 350 words. Keep the story engaging but avoid complex language, focusing on concepts and events {grade_level} students can understand."
    elif prompt_length == "long":
        prompt = f"Write a creative {movie_genre} story for {grade_level} graders over 350 words. Use vivid language and descriptive details to craft an engaging tale {grade_level} students will enjoy. Develop compelling characters and build suspense to keep readers interested. Focus on themes and situations appropriate for {grade_level}-grade students."

    response = model.predict(prompt, **parameters)
    return {"response": response.text}


@app.get("/speech")
async def generate_speech(request: Request):
    """
    Endpoint to generate speech from the story.
    """
    # Get the story from the request parameter
    story = request.query_params.get("story")

    if story is None:
        return {"error": "No story provided"}

    # Split the story into parts if it exceeds 5000 characters
    max_characters = 5000
    story_parts = [story[i:i + max_characters] for i in range(0, len(story), max_characters)]

    # Generate speech for each story part
    audio_paths = []
    for i, part in enumerate(story_parts):
        audio_path = generate_audio_from_text(part, f"output_part_{i}.mp3")
        print(audio_path)
        audio_paths.append(os.path.basename(audio_path))  # Return only the base name of the audio file

    return {"audio_paths": audio_paths}


def generate_audio_from_text(text, audio_path):
    """
    Generate audio from the input text using Google Cloud Text-to-Speech.
    """
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )
    
    output_folder = os.path.join("..", "..","FrontEndStreamlit", "audio_output")

    try:
        audio_path = os.path.join(output_folder, audio_path)  # Use the output_folder for saving the audio file
        with open(audio_path, "wb") as f:
            f.write(response.audio_content)
    except Exception as e:
        print(f"Error writing audio file: {e}")

    return audio_path


def concatenate_audio(audio_parts):
    """
    Concatenate multiple audio parts into a single audio segment.
    """
    joined_audio = AudioSegment.empty()
    for audio_part in audio_parts:
        joined_audio += audio_part
    return joined_audio

