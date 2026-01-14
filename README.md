MediMatch AI 🏥💊

AI-Powered Clinical Decision Support System

A secure, history-aware prescription analysis tool that prevents adverse drug interactions using Multimodal AI.

🚀 Overview:
- MediMatch AI acts as a second pair of eyes for patients, pharmacists, and doctors. Unlike generic chatbots, it is a structured medical workflow tool that:
- Reads Handwriting from prescription images (OCR).
- Remembers History: Checks new prescriptions against past medications to prevent cross-interaction errors.
- Validates Safety: Checks for contraindications against conditions (e.g., Pregnancy, Hypertension).
- Speeds Up Care: Provides instant "Red/Green" safety signals with clear, non-jargon explanations.

 ✨ Key Features:
- 📸 Prescription Scanning: Uses Gemini 2.5 Flash (Multimodal AI) to extract medicine names from handwritten notes.
- 🧠 History-Aware Analysis: Tracks a patient's medication timeline to detect conflicts between a new prescription and an old one (the "Amnesia Problem").
- 🌍 Multilingual Support: Generates safety alerts in English, Hindi, Spanish, or French for accessibility.
- 🎙️ Voice Dictation: Allows users/doctors to dictate symptoms instead of typing.
- 📚 Drug Reference: Built-in searchable database of thousands of medicines (seeded from FDA/Kaggle datasets).
- 📱 Progressive Web App (PWA): Installable on iOS/Android/Desktop as a native-like app.
- 🛡️ Safety Guardrails: Strict validation layer rejects non-medical images (e.g., random photos) to prevent AI hallucinations.

🛠️ Tech Stack:
- Frontend: React (SPA architecture), Tailwind CSS, FontAwesome.
- Backend: Python Flask.
- AI Engine: Google Gemini 2.5 Flash (via Google Generative AI SDK).
- Database: SQLite (Embedded, zero-config persistence).
- Deployment: Ready for Render.com / Ngrok tunneling.

⚙️ Installation & Setup:
1. Clone the Repository:
```
git clone [https://github.com/your-username/medimatch-ai.git](https://github.com/your-username/medimatch-ai.git)
cd medimatch-ai
```
2. Backend Setup:
Navigate to the backend folder and install dependencies:
```
pip install -r backend/requirements.txt
```
3. Environment Variables:
Create a .env file inside the backend/ folder and add your Gemini API Key:
```
GEMINI_API_KEY="your_google_ai_studio_key_here"
```
4. Database Seeding (Optional):
To populate the "Drug Reference" search with real data, ensure backend/drugs.csv exists. The system auto-seeds on the first run.

🚀 How to Run:
Start the Server
Run the Flask application from the root directory:
```
python backend/app.py
```

The server will start on http://0.0.0.0:5000

Access the App:
- Desktop: Open http://localhost:5000 in your browser.
- Mobile (Local Wi-Fi): Connect your phone to the same Wi-Fi and visit http://YOUR_LAPTOP_IP:5000.

Mobile (Public/Demo): Use ngrok to tunnel:
```
ngrok http 5000
```

📱 Mobile App Installation (PWA):
- Open the web app on your mobile browser (Chrome/Safari).
- Tap "Add to Home Screen" or "Install App".
- MediMatch will appear as a standalone app icon on your device.

🧪 Testing the "Time Travel" Feature:
1. Login with Patient ID: TestUser1.
2. Upload an image of "Warfarin" (or type it in notes). Run Analysis.
3. Reset/Logout.
4. Login again as TestUser1.
5. Upload an image of "Aspirin".
6. Result: The AI will warn you about the interaction with "Warfarin" from your history, even though it wasn't in the second image.

⚠️ Medical Disclaimer:
This software is a Clinical Decision Support Tool (CDST) designed for educational and verification purposes only. It does not provide medical diagnoses. All outputs must be verified by a licensed healthcare professional.

👨‍💻 Hackathon Note:
Built in 15 hours with a focus on Safety-First AI Architecture.
