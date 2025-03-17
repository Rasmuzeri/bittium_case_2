import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import styles from './styles';

function App() {
  const [message, setMessage] = useState('');
  const [conversations, setConversations] = useState(() => {
    // Load conversations from localStorage on initial render
    const savedConversations = localStorage.getItem('conversations');
    return savedConversations ? JSON.parse(savedConversations) : [
      { id: Date.now(), title: 'New Conversation', messages: [] }
    ];
  });
  const [activeConversationId, setActiveConversationId] = useState(() => {
    // Get the last active conversation or use the first one
    const savedActiveId = localStorage.getItem('activeConversationId');
    if (savedActiveId && conversations.some(conv => conv.id.toString() === savedActiveId)) {
      return parseInt(savedActiveId);
    }
    return conversations[0]?.id || Date.now();
  });
  const [chatMessages, setChatMessages] = useState(() => {
    // Load chat history from localStorage on initial render
    const activeConversation = conversations.find(conv => conv.id === activeConversationId);
    return activeConversation?.messages || [];
  });
  const [isListening, setIsListening] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    // Load dark mode preference from localStorage
    const savedMode = localStorage.getItem('darkMode');
    return savedMode ? JSON.parse(savedMode) : false;
  });
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const chatWindowRef = useRef(null);
  const [copiedMessageId, setCopiedMessageId] = useState(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chatMessages]);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('conversations', JSON.stringify(conversations));
    localStorage.setItem('activeConversationId', activeConversationId.toString());
  }, [conversations, activeConversationId]);

  // Update chatMessages when activeConversationId changes
  useEffect(() => {
    const activeConversation = conversations.find(conv => conv.id === activeConversationId);
    if (activeConversation) {
      setChatMessages(activeConversation.messages);
    } else {
      setChatMessages([]);
    }
  }, [activeConversationId, conversations]);

  // Save dark mode preference to localStorage and update body class
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    
    // Apply or remove dark-mode class on the body element
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

  // Initialize dark mode on component mount
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    }
    
    // Cleanup function to remove class when component unmounts
    return () => {
      document.body.classList.remove('dark-mode');
    };
  }, []);

  const handleSend = async () => {
    if (message.trim() === '') return;

    const newUserMessage = { text: message, sender: 'user' };
    const updatedMessages = [...chatMessages, newUserMessage];
    
    setChatMessages(updatedMessages);
    
    // Update the conversation in the conversations array
    setConversations(prevConversations => {
      return prevConversations.map(conv => {
        if (conv.id === activeConversationId) {
          // Update conversation title if it's the first message
          const title = conv.messages.length === 0 ? 
            message.substring(0, 30) + (message.length > 30 ? '...' : '') : 
            conv.title;
          
          return {
            ...conv,
            title,
            messages: updatedMessages
          };
        }
        return conv;
      });
    });

    try {
      // Start timing the request
      const startTime = performance.now();
      
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) throw new Error('Network error');

      const data = await response.json();
      
      // Calculate and log the response time
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      console.log(`Backend response time: ${responseTime.toFixed(2)}ms`);
      
      const newBotMessage = { 
        text: data.response, 
        sender: 'bot',
        responseTime: responseTime.toFixed(2) // Store the response time with the message
      };
      const finalUpdatedMessages = [...updatedMessages, newBotMessage];
      
      setChatMessages(finalUpdatedMessages);
      
      // Update the conversation with bot response
      setConversations(prevConversations => {
        return prevConversations.map(conv => {
          if (conv.id === activeConversationId) {
            return {
              ...conv,
              messages: finalUpdatedMessages
            };
          }
          return conv;
        });
      });
    } catch (error) {
      console.error('Error fetching bot response:', error);
      const errorMessage = { text: 'Error getting response.', sender: 'bot' };
      const finalUpdatedMessages = [...updatedMessages, errorMessage];
      
      setChatMessages(finalUpdatedMessages);
      
      // Update the conversation with error message
      setConversations(prevConversations => {
        return prevConversations.map(conv => {
          if (conv.id === activeConversationId) {
            return {
              ...conv,
              messages: finalUpdatedMessages
            };
          }
          return conv;
        });
      });
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

  const handleNewConversation = () => {
    const newConversation = {
      id: Date.now(),
      title: 'New Conversation',
      messages: []
    };
    
    setConversations(prev => [...prev, newConversation]);
    setActiveConversationId(newConversation.id);
    setChatMessages([]);
  };

  const handleDeleteConversation = (id, e) => {
    e.stopPropagation();
    
    setConversations(prev => {
      const filtered = prev.filter(conv => conv.id !== id);
      
      // If we're deleting the active conversation, switch to another one
      if (id === activeConversationId) {
        if (filtered.length > 0) {
          setActiveConversationId(filtered[0].id);
          setChatMessages(filtered[0].messages);
        } else {
          // If no conversations left, create a new one
          const newConversation = {
            id: Date.now(),
            title: 'New Conversation',
            messages: []
          };
          setActiveConversationId(newConversation.id);
          setChatMessages([]);
          return [newConversation];
        }
      }
      
      return filtered;
    });
  };

  const toggleSidebar = () => {
    setSidebarOpen(prev => !prev);
  };

  const toggleDarkMode = () => {
    setDarkMode(prevMode => !prevMode);
  };

  const handleCopyMessage = (text, index) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        setCopiedMessageId(index);
        setTimeout(() => setCopiedMessageId(null), 2000); // Reset after 2 seconds
      })
      .catch(err => {
        console.error('Failed to copy text: ', err);
      });
  };

  return (
    <div style={{
      ...styles.wrapper,
      backgroundColor: darkMode ? '#121212' : '#f5f5f5',
    }}>
      <div style={{
        ...styles.appContainer,
        backgroundColor: darkMode ? '#1e1e1e' : '#fff',
        boxShadow: darkMode ? '0 2px 10px rgba(255,255,255,0.1)' : '0 2px 10px rgba(0,0,0,0.1)',
      }}>
        {/* Sidebar */}
        <div style={{
          ...styles.sidebar,
          backgroundColor: darkMode ? '#252525' : '#f0f0f0',
          borderRight: darkMode ? '1px solid #444' : '1px solid #ddd',
          width: sidebarOpen ? '250px' : '0',
          display: sidebarOpen ? 'flex' : 'none',
        }}>
          <div style={{
            ...styles.sidebarHeader,
            borderBottom: darkMode ? '1px solid #444' : '1px solid #ddd',
          }}>
            <h3 style={{
              ...styles.sidebarTitle,
              color: darkMode ? '#fff' : '#333',
            }}>
              Conversations
            </h3>
            <button 
              style={{
                ...styles.newChatButton,
                backgroundColor: darkMode ? '#0a4b76' : '#007bff',
              }} 
              onClick={handleNewConversation}
            >
              + New Chat
            </button>
          </div>
          <div style={styles.conversationList}>
            {conversations.map(conv => (
              <div 
                key={conv.id}
                style={{
                  ...styles.conversationItem,
                  backgroundColor: conv.id === activeConversationId ? 
                    (darkMode ? '#3a3a3a' : '#e6e6e6') : 'transparent',
                  color: darkMode ? '#e0e0e0' : '#333',
                }}
                onClick={() => setActiveConversationId(conv.id)}
              >
                <span style={styles.conversationTitle}>{conv.title}</span>
                <button 
                  style={{
                    ...styles.deleteButton,
                    color: darkMode ? '#aaa' : '#666',
                  }}
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  title="Delete conversation"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div style={{
          ...styles.chatArea,
          width: sidebarOpen ? 'calc(100% - 250px)' : '100%',
        }}>
          <div style={{
            ...styles.header,
            backgroundColor: darkMode ? '#333' : '#f0f0f0',
            borderBottom: darkMode ? '1px solid #444' : '1px solid #ddd',
          }}>
            <div style={styles.headerLeft}>
              <button 
                style={{
                  ...styles.sidebarToggle,
                  color: darkMode ? '#fff' : '#333',
                }}
                onClick={toggleSidebar}
              >
                ☰
              </button>
              <h2 style={{
                ...styles.headerTitle,
                color: darkMode ? '#fff' : '#333',
              }}>
                Chat Assistant
              </h2>
            </div>
            <button 
              style={{
                ...styles.themeToggle,
                backgroundColor: darkMode ? '#555' : '#ddd',
              }} 
              onClick={toggleDarkMode}
            >
              {darkMode ? '☀️ Light' : '🌙 Dark'}
            </button>
          </div>
          <div 
            style={{
              ...styles.chatWindow,
              backgroundColor: darkMode ? '#2d2d2d' : '#e5ddd5',
            }} 
            ref={chatWindowRef}
          >
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
                    color: darkMode && msg.sender === 'bot' ? '#aaa' : 
                           darkMode && msg.sender === 'user' ? '#8fe3cf' : undefined,
                  }}
                >
                  {msg.sender === 'user' ? 'You' : 'AI Assistant'}
                </div>
                <div
                  style={{
                    ...styles.messageBubble,
                    ...(msg.sender === 'user' 
                      ? { 
                          ...styles.userMessage, 
                          backgroundColor: darkMode ? '#0d7e7e' : '#dcf8c6',
                          color: darkMode ? '#ffffff' : 'inherit',
                        } 
                      : { 
                          ...styles.botMessage, 
                          backgroundColor: darkMode ? '#383838' : '#fff',
                          border: darkMode ? '1px solid #555' : '1px solid #ccc',
                          color: darkMode ? '#e0e0e0' : 'inherit',
                        }),
                  }}
                >
                  {msg.sender === 'user' ? (
                    msg.text
                  ) : (
                    <ReactMarkdown
                      components={{
                        code({node, inline, className, children, ...props}) {
                          const match = /language-(\w+)/.exec(className || '')
                          return !inline ? (
                            <pre style={{
                              backgroundColor: darkMode ? '#1e1e1e' : '#f5f5f5', 
                              padding: '0.5rem',
                              borderRadius: '5px',
                              overflowX: 'auto'
                            }}>
                              <code
                                className={match ? `language-${match[1]}` : ''}
                                style={{
                                  color: darkMode ? '#e6e6e6' : '#333'
                                }}
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </code>
                            </pre>
                          ) : (
                            <code
                              className={className}
                              style={{
                                backgroundColor: darkMode ? '#2d2d2d' : '#eee',
                                padding: '2px 4px',
                                borderRadius: '3px',
                                fontSize: '0.9em'
                              }}
                              {...props}
                            >
                              {children}
                            </code>
                          )
                        },
                        p: ({children}) => <p style={{margin: '0.5rem 0'}}>{children}</p>,
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  )}
                  {/* Response time indicator for bot messages */}
                  {msg.sender === 'bot' && msg.responseTime && (
                    <div style={{
                      fontSize: '0.75rem',
                      color: darkMode ? '#888' : '#888',
                      textAlign: 'right',
                      marginTop: '4px',
                      fontStyle: 'italic'
                    }}>
                      Response time: {msg.responseTime}ms
                    </div>
                  )}
                  <button
                    className="copy-btn"
                    onClick={() => handleCopyMessage(msg.text, index)}
                    style={{
                      ...styles.copyButton,
                      backgroundColor: copiedMessageId === index ? 
                        (darkMode ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)') : 
                        (darkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'),
                      color: darkMode ? 
                        (msg.sender === 'user' ? 'rgba(255, 255, 255, 0.8)' : 'rgba(224, 224, 224, 0.8)') : 
                        'rgba(0, 0, 0, 0.6)',
                    }}
                    title="Copy to clipboard"
                  >
                    {copiedMessageId === index ? '✓ Copied' : 'Copy'}
                  </button>
                </div>
              </div>
            ))}
          </div>
          <div style={{
            ...styles.inputContainer,
            backgroundColor: darkMode ? '#1e1e1e' : '#fff',
            borderTop: darkMode ? '1px solid #444' : '1px solid #ccc',
          }}>
            <textarea
              style={{
                ...styles.textArea,
                backgroundColor: darkMode ? '#333' : '#fff',
                color: darkMode ? '#e0e0e0' : 'inherit',
                border: darkMode ? '1px solid #555' : '1px solid #ddd',
              }}
              placeholder="Type your message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <div style={styles.buttonGroup}>
              <button 
                style={{
                  ...styles.button, 
                  ...styles.resetButton,
                  backgroundColor: darkMode ? '#7d1a22' : '#dc3545',
                }} 
                onClick={handleNewConversation}
              >
                New Conversation
              </button>
              <div>
                <button 
                  style={{
                    ...styles.button,
                    backgroundColor: darkMode ? '#0a4b76' : '#007bff',
                  }} 
                  onClick={handleSend}
                >
                  Send
                </button>
                <button 
                  style={{
                    ...styles.button,
                    backgroundColor: darkMode ? '#0a4b76' : '#007bff',
                  }} 
                  onClick={handleMic}
                >
                  {isListening ? '🎤 Listening...' : '🎤'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
