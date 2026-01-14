# MediMatch AI 🏥💊

⚠️ **NOTE FOR JUDGES**: The demo is hosted on a Free Tier instance. It may take **30–50 seconds** to wake up on the first load. Please be patient.

---

## AI‑Powered Clinical Decision Support System

**MediMatch AI** is a secure, history‑aware prescription analysis tool designed to help prevent adverse drug–drug interactions using multimodal AI.
### 🔗 Quick Links
- 🌐 Live Demo: https://drug-interaction-alert-system-1.onrender.com
- 📂 GitHub Repo: https://github.com/PoojanJaviya/drug-interaction-alert-system

---

## 🚀 Overview

MediMatch AI acts as a **second pair of eyes** for patients, pharmacists, and doctors. Unlike generic chatbots, it follows a **structured medical workflow** focused on safety and clarity.

The system is designed to:

- Read handwritten prescriptions using OCR
- Remember past medications to avoid cross‑interaction errors
- Validate safety against known conditions (e.g., pregnancy, hypertension)
- Provide fast, clear **Red / Green** safety signals with non‑technical explanations

---

## ✨ Key Features

- 📸 **Prescription Scanning**\
  Extracts medicine names from handwritten prescriptions using multimodal AI.

- 🧠 **History‑Aware Analysis**\
  Maintains a medication timeline to detect conflicts between new and past prescriptions (solves the *“Amnesia Problem”*).

- 🌍 **Multilingual Support**\
  Generates safety alerts in **English, Hindi, Spanish, and French** for accessibility.

- 🎙️ **Voice Dictation**\
  Allows doctors or users to dictate symptoms instead of typing.

- 📚 **Drug Reference Module**\
  Built‑in searchable database of medicines with basic usage and side‑effect information (seeded from public datasets).

- 📱 **Progressive Web App (PWA)**\
  Installable on mobile and desktop for a native‑like experience.

- 🛡️ **Safety Guardrails**\
  Rejects non‑medical images to reduce the risk of AI hallucinations.

---

## 🛠️ Tech Stack

- **Frontend**: React (SPA architecture), Tailwind CSS, FontAwesome
- **Backend**: Python Flask
- **AI Engine**: Google Gemini 2.5 Flash (via Google Generative AI SDK)
- **Database**: SQLite (embedded, zero‑configuration persistence)
- **Deployment**: Render.com

---

## ⚙️ Installation & Setup (Local)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/medimatch-ai.git
cd medimatch-ai
```

### 2️⃣ Backend Setup

Navigate to the backend folder and install dependencies:

```bash
pip install -r backend/requirements.txt
```

### 3️⃣ Environment Variables

Create a `.env` file inside the `backend/` folder and add your API key:

```env
GEMINI_API_KEY="your_google_ai_studio_key_here"
```

### 4️⃣ Run Locally

```bash
python backend/app.py
```

The server will start on:\
`http://0.0.0.0:5000`

---

## 🧪 Testing Credentials (For Judges)

You may create your own account, or use the demo credentials below (if the database has not reset):

- **Username**: Judge
- **Password**: demo123

---

## ⚠️ Medical Disclaimer

This software is a **Clinical Decision Support Tool (CDST)** designed for educational and verification purposes only. It does **not** provide medical diagnoses or treatment recommendations. All outputs must be reviewed and confirmed by a licensed healthcare professional.

---

## 👨‍💻 Team

**Caffeine Crew** ☕

Built in **24 hours** with a strong focus on **Safety‑First AI Architecture**.

