// components/ChatWindow.tsx - Updated with complete types
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, User, Bot, Copy, Check } from 'lucide-react';
import { ChatWindowProps, Message, RCAApiRequest, RCAApiResponse } from '../types';

const ChatWindow: React.FC<ChatWindowProps> = ({
  conversation,
  onUpdateConversation,
  sidebarOpen
}) => {
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback((): void => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages, scrollToBottom]);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [input]);

  const callRCAAPI = async (message: string, history: Message[]): Promise<string> => {
    try {
      const requestBody: RCAApiRequest = {
        message,
        conversationId: conversation?.id || '',
        history: history.map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        metadata: {
          sessionId: `session_${Date.now()}`,
          analysisType: 'root_cause_analysis'
        }
      };

      const response = await fetch('/api/rca/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.REACT_APP_RCA_API_KEY || ''}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`RCA API Error: ${response.status} ${response.statusText}`);
      }

      const data: RCAApiResponse = await response.json();
      return data.analysis || data.response || 'Analysis completed successfully.';

    } catch (error) {
      console.error('RCA API Error:', error);
      return 'I apologize, but I encountered an error while analyzing your request. Please check your connection and try again.';
    }
  };

  const sendMessage = async (): Promise<void> => {
    if (!input.trim() || !conversation || isLoading) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}_user`,
      content: input.trim(),
      role: 'user',
      timestamp: new Date(),
      metadata: {
        processingTime: 0
      }
    };

    const updatedMessages = [...conversation.messages, userMessage];
    onUpdateConversation(conversation.id, updatedMessages);
    setInput('');
    setIsLoading(true);

    try {
      const startTime = Date.now();
      const response = await callRCAAPI(input.trim(), conversation.messages);
      const processingTime = Date.now() - startTime;

      const botMessage: Message = {
        id: `msg_${Date.now()}_assistant`,
        content: response,
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          processingTime,
          confidence: 0.95 // You can get this from your API response
        }
      };

      onUpdateConversation(conversation.id, [...updatedMessages, botMessage]);
    } catch (error) {
      console.error('Error in sendMessage:', error);
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        content: 'I encountered an unexpected error. Please try again later.',
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          processingTime: 0,
          confidence: 0
        }
      };
      onUpdateConversation(conversation.id, [...updatedMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text: string, messageId: string): Promise<void> => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp: Date): string => {
    return timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  if (!conversation) {
    return (
      <div className={`chat-window ${sidebarOpen ? 'with-sidebar' : 'full-width'}`}>
        <div className="empty-chat">
          <Bot size={48} />
          <h3>Welcome to RCA Agent</h3>
          <p>Start a new conversation to begin root cause analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`chat-window ${sidebarOpen ? 'with-sidebar' : 'full-width'}`}>
      <div className="chat-header">
        <h3>Root Cause Analysis Agent</h3>
        <span className="conversation-title">{conversation.title}</span>
        {conversation.messages.length > 0 && (
          <span className="message-count">
            {conversation.messages.length} messages • Updated {formatTimestamp(conversation.updatedAt || conversation.createdAt)}
          </span>
        )}
      </div>

      <div className="messages-container">
        {conversation.messages.map(message => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className="message-content">
              <div className="message-text">
                {message.content}
                {message.role === 'assistant' && (
                  <button
                    className="copy-button"
                    onClick={() => copyToClipboard(message.content, message.id)}
                    aria-label="Copy message"
                  >
                    {copiedMessageId === message.id ? (
                      <Check size={16} />
                    ) : (
                      <Copy size={16} />
                    )}
                  </button>
                )}
              </div>
              <div className="message-timestamp">
                {formatTimestamp(message.timestamp)}
                {message.metadata?.processingTime && message.metadata.processingTime > 0 && (
                  <span className="processing-time">
                    • {(message.metadata.processingTime / 1000).toFixed(1)}s
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="message-timestamp">
                Analyzing...
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe the issue for root cause analysis..."
            disabled={isLoading}
            rows={1}
            maxLength={2000}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="send-button"
            aria-label="Send message"
          >
            <Send size={20} />
          </button>
        </div>
        {input.length > 1800 && (
          <div className="character-count">
            {input.length}/2000 characters
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatWindow;
