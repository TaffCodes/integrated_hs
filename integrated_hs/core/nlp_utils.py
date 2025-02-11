# import requests
# import logging
# from .models import Insight, Diagnosis

# logger = logging.getLogger(__name__)

# # Set your Google Gemini API key and endpoint
# API_KEY = ''
# API_ENDPOINT = 'https://api.google.com/gemini/v1/insights'

# def generate_insights(diagnosis_text, diagnosis_id):
#     logger.info(f"Generating insights for diagnosis text: {diagnosis_text}")

#     # Make a request to the Google Gemini API
#     headers = {
#         'Authorization': f'Bearer {API_KEY}',
#         'Content-Type': 'application/json'
#     }
#     data = {
#         'text': diagnosis_text
#     }
#     response = requests.post(API_ENDPOINT, headers=headers, json=data)

#     # Process the response
#     if response.status_code == 200:
#         insights_data = response.json()
#         logger.info(f"API response: {insights_data}")
#         insights = {
#             "doctor_actions": insights_data.get('doctor_actions', []),
#             "patient_advice": insights_data.get('patient_advice', [])
#         }
#     else:
#         logger.error(f"Failed to generate insights: {response.status_code} {response.text}")
#         insights = {
#             "doctor_actions": [],
#             "patient_advice": []
#         }

#     logger.info(f"Generated insights: {insights}")

#     # Save insights to the database
#     try:
#         diagnosis = Diagnosis.objects.get(id=diagnosis_id)
#         Insight.objects.create(
#             diagnosis=diagnosis,
#             doctor_insights="\n".join(insights["doctor_actions"]),
#             patient_insights="\n".join(insights["patient_advice"])
#         )
#         logger.info(f"Insights saved to the database for diagnosis ID: {diagnosis_id}")
#     except Diagnosis.DoesNotExist:
#         logger.error(f"Diagnosis with ID {diagnosis_id} does not exist")

#     return insights
# ******************************************************************************************
import logging
from transformers import pipeline
from .models import Insight, Diagnosis

logger = logging.getLogger(__name__)

# Initialize the text generation pipeline with BART or T5
text_generator = pipeline("text2text-generation", model="facebook/bart-large-cnn")

def generate_insights(diagnosis_text, diagnosis_id):
    logger.info(f"Generating insights for diagnosis text: {diagnosis_text}")

    # Generate insights using BART or T5
    generated_text = text_generator(f"Generate insights for the following diagnosis: {diagnosis_text}", max_length=150, num_return_sequences=1)[0]['generated_text']
    
    # Example parsing of the generated text (you may need to adjust this based on the actual response format)
    insights = {
        "doctor_actions": [],
        "patient_advice": []
    }
    for line in generated_text.split('\n'):
        if line.startswith("Doctor Action:"):
            insights["doctor_actions"].append(line.replace("Doctor Action:", "").strip())
        elif line.startswith("Patient Advice:"):
            insights["patient_advice"].append(line.replace("Patient Advice:", "").strip())

    logger.info(f"Generated insights: {insights}")

    # Save insights to the database
    try:
        diagnosis = Diagnosis.objects.get(id=diagnosis_id)
        Insight.objects.create(
            diagnosis=diagnosis,
            doctor_insights="\n".join(insights["doctor_actions"]),
            patient_insights="\n".join(insights["patient_advice"])
        )
        logger.info(f"Insights saved to the database for diagnosis ID: {diagnosis_id}")
    except Diagnosis.DoesNotExist:
        logger.error(f"Diagnosis with ID {diagnosis_id} does not exist")

    return insights