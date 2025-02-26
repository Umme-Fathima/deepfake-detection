document.addEventListener("DOMContentLoaded", function () {
    console.log("Deepfake Video Detection Page Loaded!");

    const uploadForm = document.getElementById("uploadForm");
    const processing = document.getElementById("processing");
    const result = document.getElementById("result");
    const resultText = document.getElementById("resultText");
    const resultChartCanvas = document.getElementById("resultChart");

    if (uploadForm) {
        uploadForm.addEventListener("submit", function (event) {
            event.preventDefault();
            
            let fileInput = document.getElementById("file");
            if (fileInput.files.length === 0) {
                alert("Please select a file.");
                return;
            }

            let formData = new FormData();
            formData.append("file", fileInput.files[0]);

            // Show processing animation
            processing.classList.remove("hidden");
            result.classList.add("hidden");

            fetch("/predict", {
                method: "POST",
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Server returned an error");
                }
                return response.json();
            })
            .then(data => {
                console.log("Response Data:", data); // Debugging

                processing.classList.add("hidden");
                result.classList.remove("hidden");

                if (data.prediction) {
                    const fakeConfidence = (data.fakeConfidence * 100).toFixed(2);
                    const realConfidence = (data.realConfidence * 100).toFixed(2);

                    resultText.innerHTML = `<p>Prediction: <strong>${data.prediction}</strong></p>`;
                    
                    // Clear previous chart instance if exists
                    if (window.resultChartInstance) {
                        window.resultChartInstance.destroy();
                    }

                    // Render new chart
                    const ctx = resultChartCanvas.getContext('2d');
                    window.resultChartInstance = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: ['Fake', 'Real'],
                            datasets: [{
                                label: 'Confidence Level (%)',
                                data: [fakeConfidence, realConfidence],
                                backgroundColor: ['#8B0000', '#61ff6f'],
                                borderColor: ['#d9534f', '#5cb85c'],
                                borderWidth: 1,
                            }],
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Confidence Level (%)',
                                        color: '#ffffff',
                                        font: { size: 14 },
                                    },
                                    ticks: { color: '#ffffff' },
                                },
                                x: { ticks: { color: '#ffffff' } },
                            },
                            plugins: {
                                legend: { labels: { color: '#ffffff' } },
                                tooltip: {
                                    callbacks: {
                                        label: function (context) {
                                            return `${context.label}: ${context.raw}%`;
                                        },
                                    },
                                },
                            },
                        },
                    });
                } else {
                    resultText.innerHTML = '<p class="text-red-500">An error occurred, please try again.</p>';
                }
            })
            .catch(error => {
                console.error("Error:", error);
                processing.classList.add("hidden");
                result.classList.remove("hidden");
                resultText.innerHTML = '<p class="text-red-500">An error occurred, please try again.</p>';
            });
        });
    }


    // Review Form Validation
    const reviewForm = document.getElementById("review-form");
const feedbackResponse = document.getElementById('feedbackResponse');

if (reviewForm) {
    reviewForm.addEventListener("submit", function (event) {
        event.preventDefault();
        
        const name = document.getElementById("review-name").value.trim();
        const email = document.getElementById("review-email").value.trim();
        const message = document.getElementById("review-message").value.trim();
        const submitButton = document.querySelector("button[type='submit']"); // Get submit button

        if (!name || !email || !message) {
            feedbackResponse.innerHTML = '<p style="color: red;">All fields are required.</p>';
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = "Submitting...";

        fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, feedback: message }), // Fix: Change feedbackText to message
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                feedbackResponse.innerHTML = '<p style="color: green;">Thank you for your feedback!</p>';
                reviewForm.reset(); // Fix: Use reviewForm instead of feedbackForm
            } else {
                feedbackResponse.innerHTML = `<p style="color: red;">${data.message}</p>`;
            }
            setTimeout(() => {
                feedbackResponse.innerHTML = '';
            }, 3000);
        })
        .catch(error => {
            console.error('Error:', error);
            feedbackResponse.innerHTML = '<p style="color: red;">An error occurred while submitting your feedback. Please try again later.</p>';
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = "Submit Review";
        });
    });
}


    // Character Counter
    const reviewMessage = document.getElementById("review-message");
    const charCounter = document.getElementById("char-counter");

    if (reviewMessage && charCounter) {
        reviewMessage.addEventListener("input", function () {
            charCounter.textContent = `${this.value.length}/500`;
        });
    }

    // Click-to-Copy Email
    const copyIcon = document.getElementById("copy-icon");
    if (copyIcon) {
        copyIcon.addEventListener("click", function () {
            const emailText = document.getElementById("email-text").innerText;
            navigator.clipboard.writeText(emailText);
            const copyMessage = document.getElementById("copy-message");
            copyMessage.classList.remove("hidden");
            setTimeout(() => copyMessage.classList.add("hidden"), 2000);
        });
    }

    // Set Current Year
    const currentYear = document.getElementById("current-year");
    if (currentYear) {
        currentYear.textContent = new Date().getFullYear();
    }

    // Carousel Logic
    const carousel = document.getElementById("carousel");
    if (carousel) {
        let index = 0;
        const images = carousel.querySelectorAll("img");
        const prevBtn = document.getElementById("prev");
        const nextBtn = document.getElementById("next");

        const updateCarousel = (newIndex) => {
            images[index].classList.add("hidden");
            index = (newIndex + images.length) % images.length;
            images[index].classList.remove("hidden");
        };

        if (nextBtn) nextBtn.addEventListener("click", () => updateCarousel(index + 1));
        if (prevBtn) prevBtn.addEventListener("click", () => updateCarousel(index - 1));
    }
});

document.querySelector('.mobile-menu-btn').addEventListener('click', function() {
    document.querySelector('.mobile-menu').classList.toggle('active');
});

