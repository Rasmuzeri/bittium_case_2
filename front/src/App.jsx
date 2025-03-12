import React, { useState, useRef, useEffect } from 'react';
import styles from './styles';

function ChatInterface() {
  const [message, setMessage] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const chatWindowRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chatMessages]);

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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
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

  const handleReset = () => {
    setChatMessages([]);
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.chatContainer}>
        <div style={styles.chatWindow} ref={chatWindowRef}>
          {chatMessages.map((msg, index) => (
            <div
              key={index}
              style={{
                ...styles.messageContainer,
                ...(msg.sender === 'user' ? styles.userMessageContainer : styles.botMessageContainer),
              }}
            >
              <div 
                style={{
                  ...styles.senderName,
                  ...(msg.sender === 'user' ? styles.userSenderName : styles.botSenderName),
                }}
              >
                {msg.sender === 'user' ? 'You' : 'AI Assistant'}
              </div>
              <div
                style={{
                  ...styles.messageBubble,
                  ...(msg.sender === 'user' ? styles.userMessage : styles.botMessage),
                }}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>
        <div style={styles.inputContainer}>
          <textarea
            style={styles.textArea}
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <div style={styles.buttonGroup}>
            <button 
              style={{...styles.button, ...styles.resetButton}} 
              onClick={handleReset}
            >
              Reset Chat
            </button>
            <div>
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
    </div>
  );
}

export default ChatInterface;
