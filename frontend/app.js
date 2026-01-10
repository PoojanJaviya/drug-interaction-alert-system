// --- GLOBAL STATE ---
let GLOBAL_PATIENT_ID = null;

// --- AUTHENTICATION LOGIC ---
function handleLogin() {
    const loginInput = document.getElementById("loginId");
    const id = loginInput.value.trim();

    if (!id) {
        alert("Please enter a valid Patient ID or Name.");
        return;
    }

    // Set Global State
    GLOBAL_PATIENT_ID = id;

    // Update UI
    document.getElementById("displayUsername").innerText = id;
    document.getElementById("authOverlay").style.display = "none";
    document.getElementById("appContainer").style.display = "block";
}

function logout() {
    // Simple page reload to clear state
    window.location.reload();
}

// --- APP LOGIC ---

function handleFileSelect() {
    const fileInput = document.getElementById("imageInput");
    const fileNameSpan = document.getElementById("fileName");
    const count = fileInput.files.length;

    if (count > 0) {
        fileNameSpan.innerText = count === 1 
            ? "✅ " + fileInput.files[0].name 
            : "✅ " + count + " Prescriptions Selected";
        fileNameSpan.style.color = "#10b981"; 
        fileNameSpan.style.fontWeight = "600";
    }
}

function toggleSpeech() {
    const micBtn = document.getElementById("micBtn");
    const descInput = document.getElementById("description");

    if (!('webkitSpeechRecognition' in window)) {
        alert("Voice input not supported in this browser.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function() {
        micBtn.classList.add("mic-active");
        descInput.placeholder = "Listening...";
    };

    recognition.onend = function() {
        micBtn.classList.remove("mic-active");
        descInput.placeholder = "e.g. Patient is currently taking...";
    };

    recognition.onresult = function(event) {
        descInput.value += (descInput.value ? " " : "") + event.results[0][0].transcript;
    };

    recognition.start();
}

function resetForm() {
    document.getElementById("imageInput").value = "";
    document.getElementById("description").value = "";
    document.getElementById("fileName").innerText = "Click to Upload Prescription Image(s)";
    document.getElementById("fileName").style.color = "";
    
    document.querySelectorAll('input[name="condition"]').forEach(cb => cb.checked = false);

    document.getElementById("inputSection").style.display = "block";
    document.getElementById("loading").style.display = "none";
    document.getElementById("results").style.display = "none";
    
    document.getElementById("medsList").innerHTML = "";
    document.getElementById("alertMessage").innerText = "";
    document.getElementById("altList").innerHTML = "";
}

async function checkInteractions() {
    const fileInput = document.getElementById("imageInput");
    const descriptionInput = document.getElementById("description");
    const languageSelect = document.getElementById("languageSelect");

    const files = fileInput.files; 
    const description = descriptionInput.value.trim();
    
    // Collect Conditions
    const conditions = [];
    document.querySelectorAll('input[name="condition"]:checked').forEach(cb => {
        conditions.push(cb.value);
    });

    if (files.length === 0 && !description) {
        alert("⚠️ Action Required:\nPlease upload a prescription or enter medication details.");
        return;
    }

    // UI State Transition
    document.getElementById("inputSection").style.display = "none";
    document.getElementById("loading").style.display = "block";
    document.getElementById("results").style.display = "none";

    const formData = new FormData();
    
    for (let i = 0; i < files.length; i++) {
        formData.append("image", files[i]);
    }

    if (description) formData.append("description", description);
    formData.append("language", languageSelect.value);
    
    if (conditions.length > 0) {
        formData.append("conditions", conditions.join(", "));
    }

    // --- CRITICAL: AUTO-ATTACH PATIENT ID ---
    if (GLOBAL_PATIENT_ID) {
        formData.append("patient_id", GLOBAL_PATIENT_ID);
    }
    // ----------------------------------------

    try {
        const response = await fetch("http://localhost:5000/api/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Server error");

        const json = await response.json();

        setTimeout(() => {
            document.getElementById("loading").style.display = "none";
            document.getElementById("results").style.display = "block";
            renderResults(json.data);
        }, 800);

    } catch (error) {
        console.error("Analysis error:", error);
        document.getElementById("loading").style.display = "none";
        document.getElementById("inputSection").style.display = "block";
        alert("System Error: Unable to complete analysis.");
    }
}

function renderResults(data) {
    const riskBadge = document.getElementById("riskBadge");
    const resultCard = document.getElementById("results");

    riskBadge.innerText = data.risk_level;
    const themeColor = data.risk_hex || "#64748b"; 

    riskBadge.style.backgroundColor = themeColor;
    resultCard.style.borderLeftColor = themeColor;

    const medsList = document.getElementById("medsList");
    medsList.innerHTML = "";
    if (data.medicines_found && data.medicines_found.length > 0) {
        data.medicines_found.forEach(med => {
            const span = document.createElement("span");
            span.className = "med-tag";
            span.innerText = med;
            medsList.appendChild(span);
        });
    } else {
        medsList.innerHTML = "<span class='text-muted'>No specific medications identified</span>";
    }

    document.getElementById("alertMessage").innerText = data.alert_message;

    const altSection = document.getElementById("altSection");
    const altList = document.getElementById("altList");
    
    if (data.alternatives && data.alternatives.length > 0) {
        altSection.style.display = "block";
        altList.innerHTML = "";
        data.alternatives.forEach(alt => {
            const li = document.createElement("li");
            li.innerHTML = `<strong>Suggested:</strong> ${alt}`;
            altList.appendChild(li);
        });
    } else {
        altSection.style.display = "none";
    }
}