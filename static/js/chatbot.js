document.addEventListener("DOMContentLoaded", function() {
    // Select necessary DOM elements
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotSend = document.getElementById('chatbot-send');
    const loadingSpinner = document.getElementById('loading-spinner');

    // Function to append a message to the chat
    function appendMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        messageDiv.innerText = content;
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Function to handle message send
    function sendMessage() {
        const message = chatbotInput.value.trim();
        if (message === '') return;
        
        appendMessage(message, true);
        chatbotInput.value = '';
        loadingSpinner.classList.add('show');
        
        fetch('/chatbot/get_response/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            loadingSpinner.classList.remove('show');
            if (data.response) {
                appendMessage(data.response, false);
            } else {
                appendMessage("Sorry, I didn't understand that.", false);
            }
        })
        .catch(error => {
            loadingSpinner.classList.remove('show');
            appendMessage("Error: Could not connect to the server.", false);
        });
    }

    // Function to toggle chatbot visibility
    chatbotToggle.addEventListener('click', function() {
        chatbotContainer.classList.toggle('show');
    });

    // Send message on button click
    chatbotSend.addEventListener('click', sendMessage);

    // Send message on pressing Enter key
    chatbotInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Utility function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
