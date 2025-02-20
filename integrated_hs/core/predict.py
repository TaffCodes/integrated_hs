import os
from google.cloud import aiplatform
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the path to your service account key file
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
else:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set in the .env file")

# Initialize the AI Platform client
client = aiplatform.gapic.PredictionServiceClient()

# Define the resource name
endpoint = os.getenv("GEMINI_API_ENDPOINT")
if not endpoint:
    raise ValueError("GEMINI_API_ENDPOINT is not set in the .env file")

# Make a prediction request
response = client.predict(endpoint=endpoint, instances=[{"input": "diagnosis_text"}])

print(response)