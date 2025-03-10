import os
from groq import Groq # type: ignore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_insights(diagnosis_text):
    """
    Generate medical insights for a diagnosis using Groq API.
    
    Args:
        diagnosis_text (str): The diagnosis text to analyze.
        
    Returns:
        dict: A dictionary containing doctor actions and patient advice.
    """
    # Get the API key from environment variables
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file")
    
    # Initialize the Groq client
    client = Groq(api_key=api_key)
    
    # Create the prompt for generating insights
    prompt = f"""
    As a medical insights assistant, analyze the following diagnosis and provide:
    1. Doctor Actions: Recommend 3-5 key actions for healthcare providers (max 50 words)
    2. Patient Advice: Recommend 3-5 key points of advice for the patient (max 50 words)

    Diagnosis: {diagnosis_text}

    Format your response as follows:
    DOCTOR_ACTIONS:
    - Action 1
    - Action 2
    - Action 3

    PATIENT_ADVICE:
    - Advice 1
    - Advice 2
    - Advice 3
    """
    
    # Make the API call
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # You can also use "mixtral-8x7b" or other available models
            messages=[
                {"role": "system", "content": "You are a medical insights assistant with expertise in analyzing diagnoses and providing actionable recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        
        # Process the response
        raw_insights = response.choices[0].message.content
        
        # Parse the raw insights
        doctor_actions = []
        patient_advice = []
        
        current_section = None
        for line in raw_insights.strip().split('\n'):
            if "DOCTOR_ACTIONS:" in line:
                current_section = "doctor"
                continue
            elif "PATIENT_ADVICE:" in line:
                current_section = "patient"
                continue
            
            if line.strip().startswith('-') and current_section == "doctor":
                doctor_actions.append(line.strip()[2:].strip())
            elif line.strip().startswith('-') and current_section == "patient":
                patient_advice.append(line.strip()[2:].strip())
        
        return {
            "doctor_actions": doctor_actions,
            "patient_advice": patient_advice
        }
        
    except Exception as e:
        print(f"Error generating insights: {e}")
        return {
            "doctor_actions": [],
            "patient_advice": []
        }

if __name__ == "__main__":
    # Example usage
    diagnosis = "Stomach infestation with bacteria. Unclean food preparation surfaces. Caused by stale food. Needs inpatient for monitoring."
    insights = generate_insights(diagnosis)
    
    print("DOCTOR ACTIONS:")
    for action in insights["doctor_actions"]:
        print(f"- {action}")
    
    print("\nPATIENT ADVICE:")
    for advice in insights["patient_advice"]:
        print(f"- {advice}")