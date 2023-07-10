from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform
import vertexai
from vertexai.language_models import TextGenerationModel
import json

# Load the service account json file
# Update the values in the json file with your own
with open("FrontEndStreamlit\service_account.json") as f:
    service_account_info = json.load(f)

my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info
)

# Initialize Google AI Platform with project details and credentials
aiplatform.init(credentials=my_credentials)

with open("FrontEndStreamlit\service_account.json", encoding="utf-8") as f:
    project_json = json.load(f)
    project_id = project_json["project_id"]

# Initialize Vertex AI with project and location
vertexai.init(project=project_id, location="us-central1")

# Initialize the model
model = TextGenerationModel.from_pretrained("text-bison@001")


def generate_story(story_features):
    """
    Endpoint to generate a story based on story parameters.
    """
    # Define the model parameters
    parameters = {
        "temperature": 1,
        "max_output_tokens": 700,
        "top_p": 0.8,
        "top_k": 40
    }

    # Extract inputs from story parameters
    movie_genre = story_features.get("movie_genre", "sci-fi")
    grade_level = story_features.get("grade_level", "7")
    prompt_length = story_features.get("prompt_length", "short")

    prompt = ""

    # Construct prompt based on inputs
    if prompt_length == "short":
        prompt = f"Generate an imaginative {movie_genre} story suitable for {grade_level} graders in under 350 words. Keep the story engaging but avoid complex language, focusing on concepts and events {grade_level} students can understand."
    elif prompt_length == "long":
        prompt = f"Write a creative {movie_genre} story for {grade_level} graders over 350 words. Use vivid language and descriptive details to craft an engaging tale {grade_level} students will enjoy. Develop compelling characters and build suspense to keep readers interested. Focus on themes and situations appropriate for {grade_level}-grade students."

    response = model.predict(prompt, **parameters)
    return response.text



print(generate_story({}))
