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
        
        # 1. Add Prompt with History Context
        print(f"DEBUG: Generating prompt. Language: {language}, History Items: {len(past_history) if past_history else 0}")
        base_prompt = build_prompt(user_text, len(image_paths), language, conditions, past_history)
        inputs.append(base_prompt)

        # 2. Add All Images
        for path in image_paths:
            try:
                img = PIL.Image.open(path)
                img.load() 
                inputs.append(img)
            except Exception as img_err:
                print(f"Error loading image {path}: {img_err}")
                
        # 3. Call AI
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
    """Constructs prompt aware of language and patient conditions."""
    
    # 1. User Notes Context
    context = ""
    if user_text:
        context += f"\nUSER NOTES: '{user_text}'."
    
    # 2. History (The Key Feature)
    history_instruction = ""
    if past_history and len(past_history) > 0:
        history_instruction = f"""
        \nPATIENT MEDICATION HISTORY (Active/Recent): {', '.join(past_history)}.
        CRITICAL TASK: You MUST check for interactions between the medicines found in the NEW image(s) AND these historical medicines.
        """

    # 3. Patient Conditions Context (Crucial for safety)
    condition_instruction = ""
    if conditions:
        condition_instruction = f"\nCRITICAL PATIENT CONTEXT: The patient has these conditions: {conditions}. CHECK STRICTLY for contraindications against these."

    # 4. Language Context - MAKE THIS LOUD
    lang_instruction = ""
    if language and language.lower() != "english":
        lang_instruction = f"""
        IMPORTANT - LANGUAGE REQUIREMENT:
        The patient speaks {language}. 
        You MUST translate the 'alert_message' and 'alternatives' values into {language}.
        However, keep the 'medicines_found' names in English (or standard medical terms).
        """
    
    file_context = "image" if image_count <= 1 else f"{image_count} different prescription images"

    return f"""
    Act as a clinical toxicologist. Analyze this {file_context} and/or user notes.
    {context}
    {history_instruction}
    {condition_instruction}
    {lang_instruction}
    
    TASKS:
    1. Read the handwriting/text from ALL images provided.
    2. Identify medicine names from ALL sources.
    3. Check for drug-drug interactions across these different prescriptions.
    4. Check for drug-drug interactions between NEW medicines and PATIENT MEDICATION HISTORY.
    5. Check for contraindications based on the CRITICAL PATIENT CONTEXT provided above.
    6. Determine Risk Severity (Low, Medium, High, Critical).
    7. Write a simple alert for the patient.

    OUTPUT JSON FORMAT:
    {{
        "medicines_found": ["Meds..."],
        "risk_level": "Level",
        "risk_color": "green/yellow/orange/red",
        "alert_message": "Simple explanation...",
        "alternatives": ["Alt 1", "Alt 2"]
    }}
    """

def get_drug_interactions(inputs):
    # Added 'gemini-2.5-flash-lite' and 'gemini-1.5-flash-latest' for better fallback coverage
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

    # Return the specific error from the last model to help debug in UI
    raise Exception(f"All models failed. Last Error: {last_error}")

def get_mock_analysis():
    time.sleep(2)
    return {
        "medicines_found": ["Warfarin", "Aspirin"],
        "risk_level": "Critical",
        "risk_color": "red",
        "risk_hex": RISK_COLORS["red"],
        "alert_message": "DANGER: Taking Warfarin (from Prescription A) with Aspirin (from Prescription B) significantly increases bleeding risk.",
        "alternatives": ["Consult doctor immediately", "Consider Acetaminophen"],
        "disclaimer": "AI-generated. Verify with a doctor."
    }