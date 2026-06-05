import { useEffect, useRef, useState } from 'react';
import { FaCommentDots, FaPaperPlane, FaTimes } from 'react-icons/fa';
import { useChatbot } from '../hooks/useAdminData';
import './ChatbotWidget.css';

function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { from: 'bot', text: '¡Hola! ¿En qué puedo ayudarte hoy?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const { mutate, isPending } = useChatbot();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userText = inputValue;
    setMessages(prev => [...prev, { from: 'user', text: userText }]);
    setInputValue('');

    mutate(userText, {
      onSuccess: (response) => {
        // Tu ResponseBuilder devuelve { data: { reply: "..." } }
        const botReply = response.data?.reply || 'No recibí respuesta.';
        setMessages(prev => [...prev, { from: 'bot', text: botReply }]);
      },
      onError: (err) => {
        console.error("Chatbot Error Details:", err);
        setMessages(prev => [...prev, { 
          from: 'bot', 
          text: 'Error al conectar con el asistente.' 
        }]);
      }
    });
  };

  return (
    <>
      <button className="chat-toggle-button" onClick={toggleChat}>
        <FaCommentDots />
      </button>

      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>Asistente Virtual</h3>
            <button onClick={toggleChat}><FaTimes /></button>
          </div>
          <div className="chat-body">
            {messages.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.from}`}>
                {msg.text}
              </div>
            ))}
            {isPending && <div className="chat-message bot typing">...</div>}
            <div ref={messagesEndRef} />
          </div>
          <form className="chat-footer" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Escribe tu pregunta..."
              disabled={isPending}
            />
            <button type="submit" disabled={isPending}><FaPaperPlane /></button>
          </form>
        </div>
      )}
    </>
  );
}

export default ChatbotWidget;