// app.js
async function generateMCQs() {
    const subject = document.getElementById("subject").value;
    const mcq_count = document.getElementById("mcq_count").value;
    const tone = document.getElementById("tone").value;

    const quizDiv = document.getElementById("quiz");
    quizDiv.innerHTML = "<p>⏳ Generating MCQs...</p>";

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ subject, number: mcq_count, tone })
        });

        const data = await response.json();

        if (data.error) {
            quizDiv.innerHTML = `<p style="color:red">${data.error}</p>`;
            return;
        }

        quizDiv.innerHTML = "";

        Object.entries(data.quiz).forEach(([key, value], i) => {
            let qDiv = document.createElement("div");
            qDiv.className = "question";

            let qText = document.createElement("h3");
            qText.textContent = `${i+1}. ${value.mcq}`;
            qDiv.appendChild(qText);

            for (const [opt, val] of Object.entries(value.options)) {
                let btn = document.createElement("button");
                btn.textContent = `${opt}) ${val}`;
                btn.onclick = () => checkAnswer(opt, value.correct, btn, qDiv);
                qDiv.appendChild(btn);
            }



            quizDiv.appendChild(qDiv);
        });

    } catch (err) {
        quizDiv.innerHTML = `<p style="color:red">Error: ${err}</p>`;
    }
}

function checkAnswer(selected, correct, btn, container) {
    // Disable all buttons in this question
    const buttons = container.querySelectorAll("button");
    buttons.forEach(b => b.disabled = true);

    if (selected === correct) {
        btn.style.background = "lightgreen";
    } else {
        btn.style.background = "salmon";
        // Highlight the correct answer
        const correctBtn = Array.from(buttons).find(b => b.textContent.startsWith(correct + ")"));
        if (correctBtn) correctBtn.style.background = "lightgreen";
    }
}

