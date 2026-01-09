import os
import json
import google.generativeai as genai
import PIL.Image
import time

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_prescription_image(image_path, use_mock=False):
    """
    Analyzes image using available Gemini models.
    If use_mock=True, returns dummy data immediately.
    """
    if use_mock:
        return get_mock_analysis()

    try:
        # Load image into memory to avoid file locks
        img = PIL.Image.open(image_path)
        img.load() 
        
        return get_drug_interactions(img)

    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "risk_level": "Unknown",
            "alert_message": f"Analysis Error: {str(e)}",
            "medicines_found": []
        }

def get_drug_interactions(image_file):
    """
    Tries stable models in order: Gemini 2.5 Flash -> Gemini 1.5 Flash
    """
    
    # Priority list: 
    # 1. gemini-2.5-flash (Your best available model)
    # 2. gemini-1.5-flash (Reliable backup)
    # 3. gemini-1.5-flash-latest (Alias backup)
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-1.5-flash", 
        "gemini-1.5-flash-latest"
    ]

    prompt = """
    Act as a clinical toxicologist. Analyze this image of a prescription.
    
    TASKS:
    1. Read the handwriting to identify medicine names.
    2. Check for drug-drug interactions between them.
    3. Determine Risk Severity (Low, Medium, High, Critical).
    4. Write a simple alert for the patient.
    5. Suggest generic/safer alternatives ONLY if risk is High/Critical.

    OUTPUT JSON FORMAT:
    {
        "medicines_found": ["Meds..."],
        "risk_level": "Level",
        "risk_color": "green/yellow/orange/red",
        "alert_message": "Simple explanation...",
        "alternatives": ["Alt 1", "Alt 2"]
    }
    """

    last_error = None

    for model_name in models_to_try:
        try:
            print(f"Attempting analysis with model: {model_name}...")
            
            # We use response_mime_type for Gemini models as it enforces JSON
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            
            response = model.generate_content([prompt, image_file])
            
            # Clean JSON (Just in case)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            
            print(f"Success with {model_name}!")
            return json.loads(clean_json)

        except Exception as e:
            print(f"Failed with {model_name}: {e}")
            last_error = e
            continue

    # If all fail
    raise Exception(f"All models failed. Last Error: {last_error}")

def get_mock_analysis():
    """
    Returns fake data for frontend testing.
    """
    time.sleep(2) # Simulate network delay
    return {
        "medicines_found": ["Warfarin", "Aspirin"],
        "risk_level": "Critical",
        "risk_color": "red",
        "alert_message": "DANGER: Taking Warfarin (blood thinner) with Aspirin significantly increases the risk of internal bleeding.",
        "alternatives": ["Consult doctor immediately", "Consider Acetaminophen instead of Aspirin"],
        "disclaimer": "AI-generated. Verify with a doctor."
    }