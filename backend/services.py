import os
import json
import google.generativeai as genai
import PIL.Image
import time

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

RISK_COLORS = {
    "green": "#10b981", "yellow": "#f59e0b",
    "orange": "#f97316", "red": "#ef4444",
    "critical": "#b91c1c", "unknown": "#64748b"
}

def analyze_prescription_image(image_paths, user_text, language="English", conditions=None, past_history=None, use_mock=False):
    """
    Analyzes images + text + language + conditions + PAST HISTORY.
    """
    if use_mock:
        return get_mock_analysis()

    try:
        inputs = []
        
        print(f"DEBUG: Generating prompt. Language: {language}, History Items: {len(past_history) if past_history else 0}")
        base_prompt = build_prompt(user_text, len(image_paths), language, conditions, past_history)
        inputs.append(base_prompt)

        for path in image_paths:
            try:
                img = PIL.Image.open(path)
                img.load() 
                inputs.append(img)
            except Exception as img_err:
                print(f"Error loading image {path}: {img_err}")
                
        raw_result = get_drug_interactions(inputs)
        return process_risk_analysis(raw_result)

    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "risk_level": "Unknown",
            "alert_message": f"Analysis Error: {str(e)}",
            "medicines_found": [],
            "risk_hex": RISK_COLORS["unknown"]
        }

def process_risk_analysis(data):
    risk_color_name = data.get("risk_color", "unknown").lower()
    data["risk_hex"] = RISK_COLORS.get(risk_color_name, RISK_COLORS["unknown"])
    return data

def build_prompt(user_text, image_count, language, conditions, past_history):
    """Constructs prompt with STRICT VALIDATION."""
    
    context = ""
    if user_text:
        context += f"\nUSER NOTES: '{user_text}'."
    
    history_instruction = ""
    if past_history and len(past_history) > 0:
        history_instruction = f"""
        \nPATIENT MEDICATION HISTORY: {', '.join(past_history)}.
        CRITICAL TASK: Check interactions between NEW image content AND this history.
        """

    condition_instruction = ""
    if conditions:
        condition_instruction = f"\nCRITICAL PATIENT CONDITIONS: {conditions}. CHECK FOR CONTRAINDICATIONS."

    lang_instruction = ""
    if language and language.lower() != "english":
        lang_instruction = f"""
        IMPORTANT - LANGUAGE REQUIREMENT:
        The patient speaks {language}. 
        You MUST translate the 'alert_message' and 'alternatives' values into {language}.
        """
    
    file_context = "image" if image_count <= 1 else f"{image_count} different prescription images"

    return f"""
    Act as a clinical toxicologist. Analyze this {file_context} and/or user notes.
    {context}
    {history_instruction}
    {condition_instruction}
    {lang_instruction}
    
    TASKS:
    0. **VALIDATION (CRITICAL):** First, check if the image/text contains medical information (prescription, medicine bottle, blister pack, or clinical notes). 
       - IF THE IMAGE IS RANDOM (e.g., a cat, car, selfie, food, or blank): 
         Return "risk_level": "Unknown" and "alert_message": "No valid medical prescription or medication detected. Please upload a clear image of a prescription or medicine packaging."
         Return "medicines_found": []
         STOP THERE.
    
    1. If medical content exists: Identify medicine names.
    2. Check for drug-drug interactions.
    3. Check interactions with PATIENT HISTORY.
    4. Check contraindications with PATIENT CONDITIONS.
    5. Determine Risk Severity.
    6. Write a simple alert.

    OUTPUT JSON FORMAT:
    {{
        "medicines_found": ["Meds..."],
        "risk_level": "Level (or Unknown)",
        "risk_color": "green/yellow/orange/red",
        "alert_message": "Explanation...",
        "alternatives": ["Alt 1", "Alt 2"]
    }}
    """

def get_drug_interactions(inputs):
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite", 
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest"
    ]

    last_error = None

    for model_name in models_to_try:
        try:
            print(f"Attempting analysis with model: {model_name}...")
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            
            response = model.generate_content(inputs)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)

        except Exception as e:
            print(f"Failed with {model_name}: {e}")
            last_error = e
            continue

    raise Exception(f"All models failed. Last Error: {last_error}")

def get_mock_analysis():
    time.sleep(2)
    return {
        "medicines_found": ["Warfarin", "Aspirin"],
        "risk_level": "Critical",
        "risk_color": "red",
        "risk_hex": RISK_COLORS["red"],
        "alert_message": "DANGER: Taking Warfarin with Aspirin increases bleeding risk.",
        "alternatives": ["Consult doctor immediately"],
        "disclaimer": "AI-generated."
    }