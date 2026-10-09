const fileInput = document.getElementById("fileInput");
const analyzeBtn = document.getElementById("analyzeBtn");

const results = document.getElementById("results");
const score = document.getElementById("score");
const risklevel = document.getElementById("risklevel");
const flags = document.getElementById("flags");

analyzeBtn.addEventListener("click", async () => {

    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a labour document first.");
        return;
    }

    analyzeBtn.innerText = "ANALYZING...";
    analyzeBtn.disabled = true;

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        results.classList.remove("hidden");

        score.innerText = data.score + "%";
        risklevel.innerText = data.risk;

        flags.innerHTML = "";

        data.flags.forEach(flag => {
            const p = document.createElement("p");
            p.innerText = "⚠️ " + flag;
            flags.appendChild(p);
        });

    } catch (error) {

        alert("Something went wrong: " + error);

    }

    analyzeBtn.innerText = "RUN AI INSPECTION";
    analyzeBtn.disabled = false;
});