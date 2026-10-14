import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Button } from '../ui/Button';
import { Send, FileSearch } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './chat.css';

const ChatView = ({ documentId }) => {
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hello! I'm your AI contract assistant. Ask me anything about the document, and I'll provide an answer backed by exact citations.", citations: [] }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const query = input;
    setMessages(prev => [...prev, { role: 'user', content: query }]);
    setInput('');
    setLoading(true);

    try {
      const result = await axios.post('http://localhost:8000/api/v1/chat', { query, document_id: documentId });
      setMessages(prev => [...prev, { role: 'ai', content: result.data.response, citations: result.data.citations }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, I encountered an error while searching the document.', citations: [] }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-history">
        <AnimatePresence initial={false}>
          {messages.map((msg, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`chat-message-wrapper ${msg.role}`}
            >
              <div className={`chat-bubble ${msg.role}`}>
                <div>{msg.content}</div>
                {msg.citations && msg.citations.length > 0 && (
                  <div className="chat-citations">
                    <div style={{ width: '100%', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>SOURCES</div>
                    {msg.citations.map((cit, i) => (
                      <div key={i} className="chat-citation-chip" title={cit.snippet}>
                        <FileSearch size={12} />
                        Page {cit.page_number} {cit.section && `• Sec ${cit.section}`}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {loading && (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="chat-message-wrapper ai">
               <div className="chat-bubble ai">
                 <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                 </div>
               </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={endOfMessagesRef} />
      </div>

      <div className="chat-input-area">
        <input 
          type="text" 
          className="chat-input"
          placeholder="Ask a question about this contract..." 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <Button onClick={handleSend} disabled={loading || !input.trim()} variant="primary">
          <Send size={18} />
        </Button>
      </div>
    </div>
  );
};

export default ChatView;
