import React, { useState } from 'react';

function ChatInterface() {
  const [message, setMessage] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);

  const handleSend = async () => {
    if (message.trim() === '') return;

    const newUserMessage = { text: message, sender: 'user' };
    setChatMessages((prev) => [...prev, newUserMessage]);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) throw new Error('Network error');

      const data = await response.json();
      const newBotMessage = { text: data.response, sender: 'bot' };
      setChatMessages((prev) => [...prev, newBotMessage]);
    } catch (error) {
      console.error('Error fetching bot response:', error);
      setChatMessages((prev) => [...prev, { text: 'Error getting response.', sender: 'bot' }]);
    }

    setMessage('');
  };

  const handleMic = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Your browser does not support speech recognition.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setMessage(transcript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.chatContainer}>
        <div style={styles.chatWindow}>
          {chatMessages.map((msg, index) => (
            <div
              key={index}
              style={msg.sender === 'user' ? styles.userMessage : styles.botMessage}
            >
              {msg.text}
            </div>
          ))}
        </div>
        <div style={styles.inputContainer}>
          <textarea
            style={styles.textArea}
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <div style={styles.buttonGroup}>
            <button style={styles.button} onClick={handleSend}>
              Send
            </button>
            <button style={styles.button} onClick={handleMic}>
              {isListening ? '🎤 Listening...' : '🎤'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '20px',
  },
  chatContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '90%',
    maxWidth: '800px',
    height: '80vh',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  chatWindow: {
    flex: 1,
    padding: '20px',
    overflowY: 'auto',
    backgroundColor: '#e5ddd5',
  },
  inputContainer: {
    padding: '10px 20px',
    borderTop: '1px solid #ccc',
    backgroundColor: '#fff',
  },
  textArea: {
    width: '100%',
    height: '80px',
    padding: '10px',
    fontSize: '1rem',
    borderRadius: '4px',
    border: '1px solid #ddd',
    resize: 'none',
    marginBottom: '10px',
  },
  buttonGroup: {
    display: 'flex',
    justifyContent: 'flex-end',
  },
  button: {
    padding: '10px 20px',
    marginLeft: '10px',
    fontSize: '1rem',
    cursor: 'pointer',
    border: 'none',
    borderRadius: '4px',
    backgroundColor: '#007bff',
    color: '#fff',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#dcf8c6',
    padding: '10px',
    borderRadius: '10px',
    margin: '5px 0',
    maxWidth: '70%',
    wordWrap: 'break-word',
  },
  botMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#fff',
    padding: '10px',
    borderRadius: '10px',
    margin: '5px 0',
    maxWidth: '70%',
    border: '1px solid #ccc',
    wordWrap: 'break-word',
  },
};

export default ChatInterface;
