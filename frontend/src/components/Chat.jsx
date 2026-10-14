import React, { useState } from 'react';
import axios from 'axios';

const Chat = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSendQuery = async () => {
    if (!query) return;

    setLoading(true);
    try {
      const result = await axios.post('http://localhost:8000/api/v1/chat', { query });
      setResponse(result.data);
    } catch (error) {
      console.error('Error fetching chat response:', error);
      setResponse({ response: 'Error fetching response.', citations: [] });
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Chat</h2>
      <input
        type="text"
        value={query}
        onChange={handleQueryChange}
        placeholder="Ask a question..."
        style={{ width: '80%', padding: '10px' }}
      />
      <button onClick={handleSendQuery} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>

      {response && (
        <div style={{ marginTop: '20px' }}>
          <h3>Response</h3>
          <p>{response.response}</p>
          {response.citations && response.citations.length > 0 && (
            <div>
              <h4>Citations</h4>
              <ul>
                {response.citations.map((citation, index) => (
                  <li key={index}>
                    {citation.document_name}, Page: {citation.page_number}
                    {citation.section && `, Section: ${citation.section}`}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Chat;
