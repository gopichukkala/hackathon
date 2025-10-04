document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    const exampleContainer = document.getElementById("example-questions");
    const langSelect = document.getElementById("language-select");
    const chatbotSection = document.getElementById("chatbot-section");

    const exampleQuestions = {
        en: ["Hello", "Best crop for rice field", "What is NPK fertilizer?", "Government schemes"],
        hi: ["नमस्ते", "धान के खेत के लिए सबसे अच्छी फसल", "एनपीके उर्वरक क्या है?", "सरकारी योजनाएँ"],
        te: ["హలో", "వరి పొలానికి మంచి పంట", "ఎన్‌పీకే ఎరువు అంటే ఏమిటి?", "ప్రభుత్వ పథకాలు"],
        ta: ["வணக்கம்", "நெல் வயலுக்கு சிறந்த பயிர்", "என்என்பிகே உரம் என்ன?", "அரசு திட்டங்கள்"],
        kn: ["ನಮಸ್ಕಾರ", "ಅಕ್ಕಿ ಹೊಲಕ್ಕೆ ಉತ್ತಮ ಬೆಳೆ", "ಎನ್‌ಪಿಕೆ ಗೊಬ್ಬರವೆಂದರೆ ಏನು?", "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು"]
    };

    let currentLang = "en";

    function renderExamples() {
        exampleContainer.innerHTML = "";
        exampleQuestions[currentLang].forEach(q => {
            const btn = document.createElement("button");
            btn.textContent = q;
            btn.className = "example-btn";
            btn.addEventListener("click", () => {
                chatInput.value = q;
                chatForm.dispatchEvent(new Event("submit"));
            });
            exampleContainer.appendChild(btn);
        });
    }

    if (langSelect) {
        langSelect.addEventListener("change", () => {
            const langMap = { english: "en", hindi: "hi", telugu: "te", tamil: "ta", kannada: "kn" };
            currentLang = langMap[langSelect.value.toLowerCase()] || "en";
            renderExamples();
        });
    }

    renderExamples();

    function addMessage(sender, text) {
    const msg = document.createElement("div");
    msg.className = sender === "user" ? "user-message" : "bot-message";

    if (sender === "bot") {
        let index = 0;
        const typingSpeed = 30; // ms per letter
        msg.textContent = "";

        const typingInterval = setInterval(() => {
            msg.textContent += text.charAt(index);
            index++;
            if (index === text.length) clearInterval(typingInterval);
        }, typingSpeed);
    } else {
        msg.textContent = text;
    }

    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage("user", message);
        chatInput.value = "";

        try {
            const res = await fetch("/chat_assistant", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message, lang: currentLang })
            });

            const data = await res.json();
            if (data.reply) {
                addMessage("bot", data.reply);
            } else if (data.error) {
                addMessage("bot", "⚠️ " + data.error);
            }
        } catch (err) {
            addMessage("bot", "⚠️ Error connecting to server.");
        }
    });

    // ===== TAB SWITCHING =====
    const tabButtons = document.querySelectorAll(".nav-link"); // change this selector if needed
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const pageId = btn.getAttribute("data-page");
            chatbotSection.classList.toggle("hidden", pageId !== "chat-assistant");
        });
    });
});
