// components/ChatSidebar.tsx - Updated with complete types
import React from 'react';
import { MessageSquare, Plus, Trash2, Menu, X } from 'lucide-react';
import { ChatSidebarProps } from '../types';

const ChatSidebar: React.FC<ChatSidebarProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  isOpen,
  onToggle
}) => {
  const formatDate = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <>
      <button 
        className="mobile-toggle"
        onClick={onToggle}
        aria-label={isOpen ? "Close sidebar" : "Open sidebar"}
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
      
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>RCA Agent</h2>
          <button 
            className="new-chat-btn" 
            onClick={onNewConversation}
            aria-label="Start new conversation"
          >
            <Plus size={16} />
            New Analysis
          </button>
        </div>
        
        <div className="conversations-list">
          {conversations.map(conversation => (
            <div
              key={conversation.id}
              className={`conversation-item ${
                activeConversationId === conversation.id ? 'active' : ''
              }`}
              onClick={() => onSelectConversation(conversation.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelectConversation(conversation.id);
                }
              }}
            >
              <div className="conversation-content">
                <MessageSquare size={16} />
                <div className="conversation-info">
                  <span className="conversation-title">
                    {conversation.title}
                  </span>
                  <span className="conversation-date">
                    {formatDate(conversation.createdAt)}
                  </span>
                  <span className="message-count">
                    {conversation.messages.length} messages
                  </span>
                </div>
              </div>
              <button
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  if (window.confirm('Are you sure you want to delete this conversation?')) {
                    onDeleteConversation(conversation.id);
                  }
                }}
                aria-label="Delete conversation"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
          
          {conversations.length === 0 && (
            <div className="empty-state">
              <p>No conversations yet</p>
              <button onClick={onNewConversation}>
                Start your first RCA analysis
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ChatSidebar;
