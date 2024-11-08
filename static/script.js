document.addEventListener("DOMContentLoaded", function () {
    const applicationForm = document.getElementById("applicationForm");
    const responseSection = document.getElementById("response");
    const matchScoreDiv = document.getElementById("match-score");
    const feedbackDiv = document.getElementById("feedback");
    const suggestionsDiv = document.getElementById("suggestions");
    const chatBox = document.getElementById("chat-messages");

    // NVIDIA API Status Check
    async function checkNvidiaApiStatus() {
        const embeddingApiStatusIndicator = document.getElementById("embedding-api-status-indicator");
        const chatApiStatusIndicator = document.getElementById("chat-api-status-indicator");

        try {
            const embeddingResponse = await fetch("/check_embedding_api_status");
            const embeddingData = await embeddingResponse.json();

            if (embeddingData.status === "available") {
                embeddingApiStatusIndicator.textContent = "Embedding API: Active";
                embeddingApiStatusIndicator.style.color = "green";
            } else {
                embeddingApiStatusIndicator.textContent = "Embedding API: Unavailable";
                embeddingApiStatusIndicator.style.color = "red";
            }

            const chatResponse = await fetch("/check_chat_api_status");
            const chatData = await chatResponse.json();

            if (chatData.status === "available") {
                chatApiStatusIndicator.textContent = "Chat API: Active";
                chatApiStatusIndicator.style.color = "green";
            } else {
                chatApiStatusIndicator.textContent = "Chat API: Unavailable";
                chatApiStatusIndicator.style.color = "red";
            }
        } catch (error) {
            console.error("Error checking NVIDIA API status:", error);
            embeddingApiStatusIndicator.textContent = "Embedding API: Error";
            chatApiStatusIndicator.textContent = "Chat API: Error";
            embeddingApiStatusIndicator.style.color = "red";
            chatApiStatusIndicator.style.color = "red";
        }
    }

    checkNvidiaApiStatus();

    applicationForm.onsubmit = async function (event) {
        event.preventDefault();

        const company = document.getElementById("company").value.trim();
        const jobTitle = document.getElementById("job_title").value.trim();
        const jobDescription = document.getElementById("job_description").value.trim();
        const resumeText = document.getElementById("resume_text").value.trim();
        const resumeFile = document.getElementById("resume_file").files[0];

        if (!company || !jobTitle || !jobDescription || (!resumeText && !resumeFile)) {
            alert("Please fill in all required fields, and provide either Resume Text or upload a Resume file.");
            return;
        }

        const formData = new FormData();
        formData.append("company", company);
        formData.append("job_title", jobTitle);
        formData.append("job_description", jobDescription);
        formData.append("resume_text", resumeText);
        if (resumeFile) formData.append("resume_file", resumeFile);

        displayLoading();

        try {
            const response = await fetch("/submit_application", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Server responded with an error.");
            }

            const result = await response.json();
            displayResponse(result);

            // Initiate chat with a default message after 10 seconds
            setTimeout(() => {
                sendMessage("Can you provide feedback on my resume?", true);
            }, 10000);

        } catch (error) {
            console.error("Error during submission:", error);
            responseSection.innerHTML = `<p class="error-message">There was an error processing your request. Please try again later.</p>`;
        } finally {
            hideLoading();
        }
    };

    function displayLoading() {
        matchScoreDiv.textContent = "Calculating match score, please wait...";
        feedbackDiv.innerHTML = "";
        suggestionsDiv.innerHTML = "";
        responseSection.style.display = "block";
    }

    function hideLoading() {
        matchScoreDiv.textContent = "";
    }

    function displayResponse(result) {
        if (result.match_score !== undefined) {
            matchScoreDiv.textContent = `${result.match_score} / 100`;

            const matchScoreBar = document.getElementById("match-score-bar");
            matchScoreBar.style.width = `${result.match_score}%`;

            if (result.match_score >= 80) {
                matchScoreBar.style.backgroundColor = "#28a745"; // Green
            } else if (result.match_score >= 50) {
                matchScoreBar.style.backgroundColor = "#ffc107"; // Yellow
            } else {
                matchScoreBar.style.backgroundColor = "#dc3545"; // Red
            }

            matchScoreBar.textContent = `${result.match_score}%`;
        } else {
            matchScoreDiv.textContent = "Score unavailable.";
            document.getElementById("match-score-bar").style.width = "0";
        }

        feedbackDiv.innerHTML = result.feedback ? formatFeedback(result.feedback) : "<p>Feedback data unavailable.</p>";
        suggestionsDiv.innerHTML = result.suggestions ? formatDetailedSuggestions(result.suggestions) : "<p>No suggestions available.</p>";
    }

    function formatFeedback(feedback) {
        let feedbackHtml = `<p><strong>Assessment:</strong> ${feedback.overall_match.assessment}</p>`;

        if (feedback.keywords_analysis.missing_keywords.length > 0) {
            feedbackHtml += `<p><strong>Missing Keywords:</strong> ${feedback.keywords_analysis.missing_keywords.join(", ")}</p>`;
        }

        if (feedback.detailed_recommendations.length > 0) {
            feedbackHtml += `<p><strong>Detailed Recommendations:</strong></p><ul>`;
            feedback.detailed_recommendations.forEach(rec => {
                feedbackHtml += `<li>${rec}</li>`;
            });
            feedbackHtml += `</ul>`;
        }

        return feedbackHtml;
    }

    function formatDetailedSuggestions(suggestions) {
        let suggestionsHtml = `<p><strong>Suggestions:</strong></p><ul>`;
        suggestions.forEach(suggestion => {
            suggestionsHtml += `<li>${suggestion}</li>`;
        });
        suggestionsHtml += `</ul>`;
        return suggestionsHtml;
    }

    async function sendMessage(message, isAutoInitiated = false) {
        const chatInput = document.getElementById("chat-input");

        if (!isAutoInitiated) {
            message = chatInput.value.trim();
            if (!message) return;
            chatInput.value = "";
        }

        const userMessage = document.createElement("div");
        userMessage.className = "chat-bubble user-message";
        userMessage.textContent = message;
        chatBox.appendChild(userMessage);

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ query: message })
            });

            const data = await response.json();
            const botMessage = document.createElement("div");
            botMessage.className = "chat-bubble bot-response";
            botMessage.innerHTML = data.response || "I'm sorry, I couldn't understand that. Could you try rephrasing?";
            chatBox.appendChild(botMessage);

        } catch (error) {
            console.error("Error during chat:", error);
            const errorMessage = document.createElement("div");
            errorMessage.className = "chat-bubble bot-response";
            errorMessage.textContent = "There was an error processing your request. Please try again later.";
            chatBox.appendChild(errorMessage);
        }

        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function clearForm() {
        applicationForm.reset();
        responseSection.style.display = "none";
    }

    document.querySelector(".clear-btn").addEventListener("click", clearForm);
    document.querySelector(".chat-btn").addEventListener("click", sendMessage);
    document.getElementById("chat-input").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
});
