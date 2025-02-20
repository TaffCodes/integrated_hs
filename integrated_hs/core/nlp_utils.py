# # import requests
# # import logging
# # from .models import Insight, Diagnosis

# # logger = logging.getLogger(__name__)

# # # Set your Google Gemini API key and endpoint
# # API_KEY = ''
# # API_ENDPOINT = 'https://api.google.com/gemini/v1/insights'

# # def generate_insights(diagnosis_text, diagnosis_id):
# #     logger.info(f"Generating insights for diagnosis text: {diagnosis_text}")

# #     # Make a request to the Google Gemini API
# #     headers = {
# #         'Authorization': f'Bearer {API_KEY}',
# #         'Content-Type': 'application/json'
# #     }
# #     data = {
# #         'text': diagnosis_text
# #     }
# #     response = requests.post(API_ENDPOINT, headers=headers, json=data)

# #     # Process the response
# #     if response.status_code == 200:
# #         insights_data = response.json()
# #         logger.info(f"API response: {insights_data}")
# #         insights = {
# #             "doctor_actions": insights_data.get('doctor_actions', []),
# #             "patient_advice": insights_data.get('patient_advice', [])
# #         }
# #     else:
# #         logger.error(f"Failed to generate insights: {response.status_code} {response.text}")
# #         insights = {
# #             "doctor_actions": [],
# #             "patient_advice": []
# #         }

# #     logger.info(f"Generated insights: {insights}")

# #     # Save insights to the database
# #     try:
# #         diagnosis = Diagnosis.objects.get(id=diagnosis_id)
# #         Insight.objects.create(
# #             diagnosis=diagnosis,
# #             doctor_insights="\n".join(insights["doctor_actions"]),
# #             patient_insights="\n".join(insights["patient_advice"])
# #         )
# #         logger.info(f"Insights saved to the database for diagnosis ID: {diagnosis_id}")
# #     except Diagnosis.DoesNotExist:
# #         logger.error(f"Diagnosis with ID {diagnosis_id} does not exist")

# #     return insights
# # ******************************************************************************************
# # import logging
# # from transformers import pipeline
# # from .models import Insight, Diagnosis

# # logger = logging.getLogger(__name__)

# # # Initialize the text generation pipeline with BART or T5
# # text_generator = pipeline("text2text-generation", model="facebook/bart-large-cnn")

# # def generate_insights(diagnosis_text, diagnosis_id):
# #     logger.info(f"Generating insights for diagnosis text: {diagnosis_text}")

# #     # Generate insights using BART or T5
# #     generated_text = text_generator(f"Generate insights for the following diagnosis: {diagnosis_text}", max_length=150, num_return_sequences=1)[0]['generated_text']
    
# #     # Example parsing of the generated text (you may need to adjust this based on the actual response format)
# #     insights = {
# #         "doctor_actions": [],
# #         "patient_advice": []
# #     }
# #     for line in generated_text.split('\n'):
# #         if line.startswith("Doctor Action:"):
# #             insights["doctor_actions"].append(line.replace("Doctor Action:", "").strip())
# #         elif line.startswith("Patient Advice:"):
# #             insights["patient_advice"].append(line.replace("Patient Advice:", "").strip())

# #     logger.info(f"Generated insights: {insights}")

# #     # Save insights to the database
# #     try:
# #         diagnosis = Diagnosis.objects.get(id=diagnosis_id)
# #         Insight.objects.create(
# #             diagnosis=diagnosis,
# #             doctor_insights="\n".join(insights["doctor_actions"]),
# #             patient_insights="\n".join(insights["patient_advice"])
# #         )
# #         logger.info(f"Insights saved to the database for diagnosis ID: {diagnosis_id}")
# #     except Diagnosis.DoesNotExist:
# #         logger.error(f"Diagnosis with ID {diagnosis_id} does not exist")

# #     return insights

# # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# # import os
# # import requests
# # import json
# # from dotenv import load_dotenv

# # load_dotenv()

# # API_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # Your service account JSON key file
# # API_ENDPOINT = os.getenv("GEMINI_API_ENDPOINT") # The endpoint from Vertex AI

# # def generate_insights(diagnosis_text):
# #     headers = {
# #         'Authorization': f'Bearer {API_KEY}',
# #         'Content-Type': 'application/json'
# #     }

# #     data = {
# #         "instances": [{"content": f"Generate doctor actions and patient advice based on the following diagnosis: {diagnosis_text}"}], # Your prompt here!
# #         "parameters": {} # Add any parameters as needed
# #     }

# #     response = requests.post(API_ENDPOINT, headers=headers, json=data)

# #     if response.status_code == 200:
# #         insights = response.json()
# #         # Extract the doctor actions and patient advice from the response.
# #         # The exact structure depends on the API response format.
# #         # This is an example, adapt it as needed:
# #         try:
# #             predictions = insights["predictions"][0]  # Get the first prediction
# #             doctor_actions = predictions.get("doctor_actions", [])  # Extract doctor actions
# #             patient_advice = predictions.get("patient_advice", []) # Extract patient advice
# #             return {"doctor_actions": doctor_actions, "patient_advice": patient_advice}
# #         except (KeyError, IndexError):
# #             print(f"Error extracting insights from response: {insights}")
# #             return {"doctor_actions": [], "patient_advice": []}

# #     else:
# #         print(f"Error: {response.status_code} - {response.text}")
# #         return {"doctor_actions": [], "patient_advice": []}


# # Example usage:
# # diagnosis = "The patient presents with persistent cough and fever.  Chest X-ray indicates possible pneumonia."
# # insights = generate_insights(diagnosis)
# # print(insights)





# from google import genai
# from google.genai import types
# import base64

# def generate_insights():
#   client = genai.Client(
#       vertexai=True,
#       project="integrated-hms",
#       location="us-central1",
#   )

#   text1 = types.Part.from_text(text="""Generate insights for both doctor actions and patient advice for the following diagnosis(50 words max for each) : Stomach infestation with bacteria Unclean food preparation surfaces Caused by stale food Needs inpatient for monitoring""")

#   model = "gemini-2.0-flash-001"
#   contents = [
#     types.Content(
#       role="user",
#       parts=[
#         text1
#       ]
#     )
#   ]
#   generate_content_config = types.GenerateContentConfig(
#     temperature = 1,
#     top_p = 0.95,
#     max_output_tokens = 8192,
#     response_modalities = ["TEXT"],
#     safety_settings = [types.SafetySetting(
#       category="HARM_CATEGORY_HATE_SPEECH",
#       threshold="OFF"
#     ),types.SafetySetting(
#       category="HARM_CATEGORY_DANGEROUS_CONTENT",
#       threshold="OFF"
#     ),types.SafetySetting(
#       category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
#       threshold="OFF"
#     ),types.SafetySetting(
#       category="HARM_CATEGORY_HARASSMENT",
#       threshold="OFF"
#     )],
#   )

#   for chunk in client.models.generate_content_stream(
#     model = model,
#     contents = contents,
#     config = generate_content_config,
#     ):
#     print(chunk.text, end="")

# generate_insights()