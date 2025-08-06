// components/ChatWindow.tsx - Simplified to remove duplicate API handling
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, User, Bot, Copy, Check } from 'lucide-react';
import { Message } from '../types';

interface ChatWindowProps {
  conversation: any; // Using any for now to avoid type issues
  onUpdateConversation: (id: string, messages: Message[]) => void;
  sidebarOpen: boolean;
  isLoading?: boolean; // Add loading prop
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  conversation,
  onUpdateConversation,
  sidebarOpen,
  isLoading = false
}) => {
  const [input, setInput] = useState<string>('');
  const [localLoading, setLocalLoading] = useState<boolean>(false);
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
      const requestBody = {
        message,
        conversationId: conversation?.id || '',
        history: history.slice(0, -1).map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        metadata: {
          sessionId: `session_${Date.now()}`,
          analysisType: conversation?.jiraId ? 'jira_investigation' : 'general',
          jiraId: conversation?.jiraId
        }
      };

      console.log('ChatWindow API call:', requestBody); // Debug log

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

      const data = await response.json();
      return data.analysis || data.response || 'Analysis completed successfully.';

    } catch (error) {
      console.error('RCA API Error:', error);
      return 'I apologize, but I encountered an error while analyzing your request. Please check your connection and try again.';
    }
  };

  const sendMessage = async (): Promise<void> => {
    if (!input.trim() || !conversation || localLoading || isLoading) return;

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
    setLocalLoading(true);

    try {
      const startTime = Date.now();
      const response = await callRCAAPI(input.trim(), updatedMessages);
      const processingTime = Date.now() - startTime;

      const botMessage: Message = {
        id: `msg_${Date.now()}_assistant`,
        content: response,
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          processingTime,
          confidence: 0.95
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
      setLocalLoading(false);
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
          <p>Click "New Analysis" to start investigating a JIRA ticket</p>
        </div>
      </div>
    );
  }

  const isAnyLoading = isLoading || localLoading;

  return (
    <div className={`chat-window ${sidebarOpen ? 'with-sidebar' : 'full-width'}`}>
      <div className="chat-header">
        <h3>Root Cause Analysis Agent</h3>
        <span className="conversation-title">
          {conversation.jiraId ? `JIRA: ${conversation.jiraId}` : conversation.title}
        </span>
        {conversation.messages.length > 0 && (
          <span className="message-count">
            {conversation.messages.length} messages • Updated {formatTimestamp(conversation.updatedAt || conversation.createdAt)}
          </span>
        )}
      </div>

      <div className="messages-container">
        {conversation.messages.map((message: Message) => (
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
        
        {isAnyLoading && (
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
                {isLoading ? 'Starting analysis...' : 'Analyzing...'}
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
            placeholder={
              conversation.jiraId 
                ? `Continue analyzing JIRA ${conversation.jiraId}...` 
                : "Ask follow-up questions about the analysis..."
            }
            disabled={isAnyLoading}
            rows={1}
            maxLength={2000}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isAnyLoading}
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
