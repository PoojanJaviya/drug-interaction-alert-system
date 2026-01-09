import os
import json
import google.generativeai as genai
import PIL.Image
import time

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- BUSINESS LOGIC: Color Mappings ---
# We define the visual identity here in the backend
RISK_COLORS = {
    "green": "#10b981",   # Emerald
    "yellow": "#f59e0b",  # Amber
    "orange": "#f97316",  # Orange
    "red": "#ef4444",     # Red
    "critical": "#b91c1c", # Dark Red
    "unknown": "#64748b"  # Slate
}

def analyze_prescription_image(image_path, user_text, use_mock=False):
    """
    Analyzes image + optional user text using Gemini.
    """
    if use_mock:
        return get_mock_analysis()

    try:
        inputs = []
        
        # Add Prompt first
        base_prompt = build_prompt(user_text)
        inputs.append(base_prompt)

        # Add Image if provided
        if image_path:
            img = PIL.Image.open(image_path)
            img.load() 
            inputs.append(img)
        
        raw_result = get_drug_interactions(inputs)
        
        # Post-process: Add UI-ready hex codes here
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
    """
    Enhances the AI response with UI-ready attributes (Hex codes).
    """
    risk_color_name = data.get("risk_color", "unknown").lower()
    
    # Logic: Map the named color to the specific Hex Code
    # Default to slate gray if unknown
    data["risk_hex"] = RISK_COLORS.get(risk_color_name, RISK_COLORS["unknown"])
    
    return data

def build_prompt(user_text):
    """Constructs the prompt with user context."""
    context = ""
    if user_text:
        context = f"\nUSER NOTES/SYMPTOMS: The user also provided this context: '{user_text}'. Consider this in your analysis."

    return f"""
    Act as a clinical toxicologist. Analyze this prescription image and/or user notes.
    {context}
    
    TASKS:
    1. Read the handwriting to identify medicine names.
    2. Check for drug-drug interactions between them.
    3. Determine Risk Severity (Low, Medium, High, Critical).
    4. Write a simple alert for the patient.
    5. Suggest generic/safer alternatives ONLY if risk is High/Critical.

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
    """
    Tries stable models. Inputs is a list [prompt, image].
    """
    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]

    for model_name in models_to_try:
        try:
            print(f"Attempting analysis with model: {model_name}...")
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            
            response = model.generate_content(inputs)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            
            print(f"Success with {model_name}!")
            return json.loads(clean_json)

        except Exception as e:
            print(f"Failed with {model_name}: {e}")
            continue

    raise Exception("All models failed.")

def get_mock_analysis():
    time.sleep(2)
    return {
        "medicines_found": ["Warfarin", "Aspirin"],
        "risk_level": "Critical",
        "risk_color": "red",
        "risk_hex": RISK_COLORS["red"],
        "alert_message": "DANGER: Taking Warfarin (blood thinner) with Aspirin significantly increases the risk of internal bleeding.",
        "alternatives": ["Consult doctor immediately", "Consider Acetaminophen instead of Aspirin"],
        "disclaimer": "AI-generated. Verify with a doctor."
    }