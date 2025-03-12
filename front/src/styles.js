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
    display: 'flex',
    flexDirection: 'column',
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
    boxSizing: 'border-box',
  },
  buttonGroup: {
    display: 'flex',
    justifyContent: 'space-between',
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
  resetButton: {
    backgroundColor: '#dc3545',
  },
  messageContainer: {
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '70%',
    margin: '5px 0',
    wordWrap: 'break-word',
  },
  userMessageContainer: {
    alignSelf: 'flex-end',
  },
  botMessageContainer: {
    alignSelf: 'flex-start',
  },
  messageBubble: {
    padding: '10px',
    borderRadius: '10px',
  },
  userMessage: {
    backgroundColor: '#dcf8c6',
    alignSelf: 'flex-end',
  },
  botMessage: {
    backgroundColor: '#fff',
    border: '1px solid #ccc',
  },
  senderName: {
    fontSize: '0.8rem',
    marginBottom: '2px',
    fontWeight: 'bold',
  },
  userSenderName: {
    textAlign: 'right',
    color: '#4a6c40',
  },
  botSenderName: {
    color: '#666',
  },
};

export default styles; 