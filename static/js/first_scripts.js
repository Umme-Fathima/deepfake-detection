const uploadForm = document.getElementById('uploadForm');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const resultChart = document.getElementById('resultChart');
    let resultChartInstance; // To store the Chart.js instance

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
    
        resultDiv.innerHTML = '';
        if(resultChartInstance){
            resultChartInstance.destroy();
        }
        loadingDiv.style.display = 'block';
    
        const formData = new FormData(uploadForm);
        fetch('/predict', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loadingDiv.style.display = 'none';
            if (data.prediction) {
                const fakeConfidence = data.fakeConfidence * 100;
                const realConfidence = data.realConfidence * 100;
                resultDiv.innerHTML = `<p>${data.prediction}</p>`;
                // Render a new chart
                const ctx = document.getElementById('resultChart').getContext('2d');
                resultChartInstance = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Fake', 'Real'],
                        datasets: [
                            {
                                label: 'Confidence Level (%)',
                                data: [fakeConfidence, realConfidence],
                                backgroundColor: ['#8B0000', '#61ff6f'],
                                borderColor: ['#d9534f', '#5cb85c'],
                                borderWidth: 1,
                            },
                        ],
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
                                    font: {
                                        size: 14,
                                    },
                                },
                                ticks: {
                                    color: '#ffffff',
                                },
                            },
                            x: {
                                ticks: {
                                    color: '#ffffff',
                                },
                            },
                        },
                        plugins: {
                            legend: {
                                labels: {
                                    color: '#ffffff',
                                },
                            },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        return `${context.label}: ${context.raw.toFixed(2)}%`;
                                    },
                                },
                            },
                        },
                    },
                });
                
            } else {
                resultDiv.innerHTML = '<p>An error occurred, please try again.</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingDiv.style.display = 'none';
            resultDiv.innerHTML = '<p>An error occurred, please try again.</p>';
        });
    });
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackResponse = document.getElementById('feedbackResponse');

    feedbackForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const feedbackText = document.getElementById('feedbackText').value;

        if (!name.trim() || !email.trim() || !feedbackText.trim()) {
            feedbackResponse.innerHTML = '<p style="color: red;">All fields are required.</p>';
            return;
        }

        feedbackResponse.innerHTML = 'Submitting your feedback...';

        fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, feedback: feedbackText }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                feedbackResponse.innerHTML = '<p style="color: green;">Thank you for your feedback!</p>';
                feedbackForm.reset();
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
        });
    });
    
    let slideIndex = 0;
    showSlides();
    
    // Function to display the current slide
    function showSlides() {
        let slides = document.getElementsByClassName("mySlides");
        for (let i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";  
        }
        slides[slideIndex].style.display = "block";  
    }
    
    // Function to change slide manually
    function plusSlides(n) {
        slideIndex += n;
        let slides = document.getElementsByClassName("mySlides");
        if (slideIndex >= slides.length) { slideIndex = 0 }
        if (slideIndex < 0) { slideIndex = slides.length - 1 }
        showSlides();
    }
    
    function openNav() {
        document.getElementById("sideNav").style.width = "250px";
    }
    
    function closeNav() {
        document.getElementById("sideNav").style.width = "0";
    }

    
    