// UI: Handle File Selection Feedback
function handleFileSelect() {
    const fileInput = document.getElementById("imageInput");
    const fileNameSpan = document.getElementById("fileName");
    
    if (fileInput.files.length > 0) {
        fileNameSpan.innerText = "✅ " + fileInput.files[0].name;
        fileNameSpan.style.color = "#10b981"; // Keep UI feedback green
        fileNameSpan.style.fontWeight = "600";
    }
}

// FEATURE: Voice Dictation (Browser API)
function toggleSpeech() {
    const micBtn = document.getElementById("micBtn");
    const descInput = document.getElementById("description");

    if (!('webkitSpeechRecognition' in window)) {
        alert("Voice input is not supported in this browser. Try Chrome or Edge.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function() {
        micBtn.classList.add("mic-active");
        descInput.placeholder = "Listening... Speak now.";
    };

    recognition.onend = function() {
        micBtn.classList.remove("mic-active");
        descInput.placeholder = "e.g. Patient is currently taking Amoxicillin...";
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        // Append text naturally
        descInput.value += (descInput.value ? " " : "") + transcript;
    };

    recognition.start();
}

// UI: Reset the Interface
function resetForm() {
    // Inputs
    document.getElementById("imageInput").value = "";
    document.getElementById("description").value = "";
    document.getElementById("fileName").innerText = "Click to Upload Prescription Image";
    document.getElementById("fileName").style.color = "";

    // Sections
    document.getElementById("inputSection").style.display = "block";
    document.getElementById("loading").style.display = "none";
    document.getElementById("results").style.display = "none";
    
    // Content
    document.getElementById("medsList").innerHTML = "";
    document.getElementById("alertMessage").innerText = "";
    document.getElementById("altList").innerHTML = "";
}

// API: Main Logic
async function checkInteractions() {
    const fileInput = document.getElementById("imageInput");
    const descriptionInput = document.getElementById("description");

    const file = fileInput.files[0];
    const description = descriptionInput.value.trim();

    // Validation
    if (!file && !description) {
        alert("⚠️ Action Required:\nPlease upload a prescription image OR enter medication details.");
        return;
    }

    // Switch to Loading State
    const inputSection = document.getElementById("inputSection");
    const loading = document.getElementById("loading");
    const results = document.getElementById("results");

    inputSection.style.display = "none";
    loading.style.display = "block";
    results.style.display = "none";

    const formData = new FormData();
    if (file) formData.append("image", file);
    if (description) formData.append("description", description);

    try {
        const response = await fetch("http://localhost:5000/api/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Server error");

        const json = await response.json();

        // Artificial delay for UX smoothness
        setTimeout(() => {
            loading.style.display = "none";
            results.style.display = "block";
            renderResults(json.data);
        }, 800);

    } catch (error) {
        console.error("Analysis error:", error);
        loading.style.display = "none";
        inputSection.style.display = "block";
        alert("System Error: Unable to complete analysis. Please try again.");
    }
}

// UI: Display Data (No Business Logic here!)
function renderResults(data) {
    const resultCard = document.getElementById("results");
    const riskBadge = document.getElementById("riskBadge");

    // 1. Apply Risk Data directly from Backend
    riskBadge.innerText = data.risk_level;
    
    // Use the Hex Code calculated by Python
    const themeColor = data.risk_hex || "#64748b"; // Fallback to slate

    riskBadge.style.backgroundColor = themeColor;
    resultCard.style.borderLeftColor = themeColor;

    // 2. Render Medicines
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

    // 3. Render Alert
    document.getElementById("alertMessage").innerText = data.alert_message;

    // 4. Render Alternatives
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