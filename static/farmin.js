document.addEventListener('DOMContentLoaded', () => {
    const BASE_URL = "http://127.0.0.1:5000"; // <-- Flask backend URL

    const tabButtons = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    const setLoading = (selector, msg = "Loading...") => {
        document.querySelector(selector).innerHTML = `<p>${msg}</p>`;
    };

    // ======= TAB SWITCHING =======
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const pageId = btn.getAttribute('data-page');

            pages.forEach(page => {
                page.classList.remove('active');
                if (page.id === pageId) page.classList.add('active');
            });

            if (pageId === "market-prices") loadMarketPrices();
        });
    });

    // 🔹 NEW: Trigger the first active tab on page load
    const initialActiveTab = document.querySelector('.nav-link.active');
    if (initialActiveTab) initialActiveTab.click();

    // ======= LANGUAGE TRANSLATION =======
    document.getElementById("translate-btn")?.addEventListener("click", async () => {
        const lang = document.getElementById("language-select").value;
        const allTextElements = document.querySelectorAll("[data-lang-key]");

        try {
            await Promise.all([...allTextElements].map(async el => {
                const text = el.textContent.trim();
                if (!text) return;
                const response = await fetch(`${BASE_URL}/translate`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text, lang })
                });
                const data = await response.json();
                if (data.translation) el.textContent = data.translation;
            }));
        } catch (err) {
            console.error("Translation error:", err);
            alert("Translation service unavailable.");
        }
    });

    // ======= LOGIN =======
    document.getElementById("login-btn")?.addEventListener("click", async () => {
        const username = document.getElementById("login-username").value;
        const password = document.getElementById("login-password").value;
        try {
            const res = await fetch(`${BASE_URL}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            document.getElementById("login-result").innerText = data.message || data.error;
        } catch (err) {
            document.getElementById("login-result").innerText = "Login failed.";
        }
    });

    // ======= SIGNUP =======
    document.getElementById("signup-btn")?.addEventListener("click", async () => {
        const username = document.getElementById("signup-username").value;
        const password = document.getElementById("signup-password").value;
        try {
            const res = await fetch(`${BASE_URL}/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            document.getElementById("signup-result").innerText = data.message || data.error;
        } catch (err) {
            document.getElementById("signup-result").innerText = "Signup failed.";
        }
    });

    // ======= UPLOAD SOIL REPORT =======
    document.getElementById('upload-btn')?.addEventListener('click', async () => {
        const fileInput = document.getElementById('soil-file');
        if (!fileInput.files.length) return alert("Please upload a soil report.");
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("soil_report", file);

        setLoading("#crop-recommendation .results-container");

        try {
            const response = await fetch(`${BASE_URL}/upload_soil_report`, { method: "POST", body: formData });
            const data = await response.json();

            let soilValuesHtml = "";
            for (const [key, value] of Object.entries(data.values || {})) {
                soilValuesHtml += `<tr><td>${key.replace(/_/g, " ")}</td><td>${value ?? "-"}</td></tr>`;
            }

            let recommendationsHtml = "";
            (data.recommended_crops || []).forEach(crop => {
                recommendationsHtml += `<li>${crop}</li>`;
            });

            document.querySelector("#crop-recommendation .results-container").innerHTML = `
                <div class="soil-report-dashboard">
                    <h3 data-lang-key="Soil Report">Soil Report</h3>
                    <div class="report-section">
                        <h4 data-lang-key="Report Type">Report Type:</h4>
                        <p>${data.report_type || "default"}</p>
                    </div>
                    <div class="soil-values-section">
                        <h4 data-lang-key="Soil Parameters">Soil Parameters</h4>
                        <table>${soilValuesHtml}</table>
                    </div>
                    <div class="recommendations-section">
                        <h4 data-lang-key="Recommendations">Recommendations</h4>
                        <ul>${recommendationsHtml}</ul>
                    </div>
                </div>`;
        } catch (err) {
            document.querySelector("#crop-recommendation .results-container").innerHTML = "<p>Error processing soil report.</p>";
        }
    });

    // ======= CROP RECOMMENDATION =======
    document.getElementById('crop-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const soil = document.querySelector("select[name=soil]").value;
        const season = document.querySelector("select[name=season]").value;
        const water = document.querySelector("select[name=water]").value;
        const location = document.querySelector("input[name=location]").value;

        setLoading("#crop-recommendation .results-container");

        try {
            const response = await fetch(`${BASE_URL}/recommend_crop`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ soil, season, water, location })
            });
            const result = await response.json();
            document.querySelector("#crop-recommendation .results-container").innerHTML =
                `<h3 data-lang-key="Recommended Crops">Recommended Crops</h3>
                 <p>${(result.recommended_crops || []).join(", ")}</p>`;
        } catch (err) {
            document.querySelector("#crop-recommendation .results-container").innerHTML = "<p>Error recommending crops.</p>";
        }
    });

    // ======= DISEASE DETECTION =======
    document.getElementById('detect-disease-btn')?.addEventListener('click', async () => {
        const fileInput = document.getElementById('leaf-file');
        if (!fileInput.files.length) return alert("Please upload a leaf image.");
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("leaf_image", file);

        const resultContainer = document.querySelector("#disease-detection .results-container");
        resultContainer.innerHTML = "<p>Loading...</p>";

        try {
            const response = await fetch(`${BASE_URL}/detect_disease`, { method: "POST", body: formData });
            const data = await response.json();
            resultContainer.innerHTML = `
                <h3 data-lang-key="Disease Result">Disease Result</h3>
                <p>${data.result || data.error}</p>
            `;
        } catch (err) {
            resultContainer.innerHTML = "<p>Error detecting disease.</p>";
        }
    });

    // ======= MARKET PRICES =======
    const loadMarketPrices = async () => {
        const container = document.getElementById("prices-container");
        container.style.display = "block";
        container.innerHTML = "<p>Loading...</p>";

        try {
            const response = await fetch(`${BASE_URL}/market_prices`);
            let data = await response.json();

            if (!data || Object.keys(data).length === 0) {
                data = { "Rice": 2400, "Wheat": 1950, "Maize": 1800, "Sugarcane": 3000 };
            }

            let html = `
                <table class="market-prices-table">
                    <thead>
                        <tr>
                            <th>Crop</th>
                            <th>Price (₹ per quintal)</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            for (let crop in data) {
                html += `<tr><td>${crop}</td><td>₹${data[crop]}</td></tr>`;
            }
            html += `</tbody></table>`;
            container.innerHTML = html;
        } catch (err) {
            console.error(err);
            container.innerHTML = "<p>Error fetching prices.</p>";
        }
    };
    document.getElementById('fetch-prices-btn')?.addEventListener('click', loadMarketPrices);

    // ======= CHAT ASSISTANT =======
    document.getElementById('chat-send-btn')?.addEventListener('click', async () => {
        const msg = document.getElementById('chat-input').value.trim();
        if (!msg) return;
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML += `<div><b>You:</b> ${msg}</div>`;
        document.getElementById('chat-input').value = "";

        try {
            const response = await fetch(`${BASE_URL}/chat_assistant`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            });
            if (!response.ok) {
                const errorData = await response.json();
                console.error("Chat assistant error:", errorData);
                chatBox.innerHTML += `<div><b>Bot:</b> Error: ${errorData.error || "Unknown error"}</div>`;
                return;
            }
            const data = await response.json();
            chatBox.innerHTML += `<div><b>Bot:</b> ${data.reply || "No response"}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        } catch (err) {
            console.error("Fetch error:", err);
            chatBox.innerHTML += `<div><b>Bot:</b> Error contacting assistant.</div>`;
        }
    });

    // ======= CAROUSEL FEATURE =======
    const track = document.querySelector('.carousel-track');
    if (track) {
        const slides = Array.from(track.children);
        const nextButton = document.querySelector('.next-btn');
        const prevButton = document.querySelector('.prev-btn');
        let currentIndex = 0;

        function updateCarousel() {
            const slideWidth = slides[0].getBoundingClientRect().width;
            track.style.transform = `translateX(-${slideWidth * currentIndex}px)`;
        }

        nextButton?.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % slides.length;
            updateCarousel();
        });

        prevButton?.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            updateCarousel();
        });

        window.addEventListener('resize', updateCarousel);
        updateCarousel();
    }
});
