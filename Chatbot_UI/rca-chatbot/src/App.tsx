// App.tsx - Updated with complete type definitions
import React, { useState, useEffect } from 'react';
import ChatSidebar from './components/ChatSidebar';
import ChatWindow from './components/ChatWindow';
import { Conversation, Message, AppState } from './types';
import './App.css';

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    conversations: [],
    activeConversationId: null,
    sidebarOpen: true,
    isLoading: false
  });

  // Load conversations from localStorage on app start
  useEffect(() => {
    const savedConversations = localStorage.getItem('rca-conversations');
    if (savedConversations) {
      try {
        const parsed = JSON.parse(savedConversations);
        const conversationsWithDates = parsed.map((conv: any) => ({
          ...conv,
          createdAt: new Date(conv.createdAt),
          updatedAt: conv.updatedAt ? new Date(conv.updatedAt) : undefined,
          messages: conv.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }));
        setState(prev => ({
          ...prev,
          conversations: conversationsWithDates
        }));
      } catch (error) {
        console.error('Error loading conversations:', error);
      }
    }
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (state.conversations.length > 0) {
      localStorage.setItem('rca-conversations', JSON.stringify(state.conversations));
    }
  }, [state.conversations]);

  const createNewConversation = (): void => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New RCA Analysis',
      messages: [],
      createdAt: new Date(),
      metadata: {
        totalMessages: 0,
        status: 'active',
        analysisType: 'general'
      }
    };

    setState(prev => ({
      ...prev,
      conversations: [newConversation, ...prev.conversations],
      activeConversationId: newConversation.id
    }));
  };

  const deleteConversation = (id: string): void => {
    setState(prev => ({
      ...prev,
      conversations: prev.conversations.filter(conv => conv.id !== id),
      activeConversationId: prev.activeConversationId === id ? null : prev.activeConversationId
    }));
  };

  const updateConversation = (id: string, messages: Message[]): void => {
    setState(prev => ({
      ...prev,
      conversations: prev.conversations.map(conv => 
        conv.id === id 
          ? { 
              ...conv, 
              messages,
              title: messages.length > 0 
                ? messages[0].content.substring(0, 50) + (messages[0].content.length > 50 ? '...' : '')
                : 'New RCA Analysis',
              updatedAt: new Date(),
              metadata: {
                ...conv.metadata,
                totalMessages: messages.length,
                status: messages.length > 0 ? 'active' as const : 'pending' as const
              }
            }
          : conv
      )
    }));
  };

  const setActiveConversationId = (id: string | null): void => {
    setState(prev => ({
      ...prev,
      activeConversationId: id
    }));
  };

  const toggleSidebar = (): void => {
    setState(prev => ({
      ...prev,
      sidebarOpen: !prev.sidebarOpen
    }));
  };

  const activeConversation = state.conversations.find(c => c.id === state.activeConversationId);

  return (
    <div className="app">
      <ChatSidebar
        conversations={state.conversations}
        activeConversationId={state.activeConversationId}
        onSelectConversation={setActiveConversationId}
        onNewConversation={createNewConversation}
        onDeleteConversation={deleteConversation}
        isOpen={state.sidebarOpen}
        onToggle={toggleSidebar}
      />
      <ChatWindow
        conversation={activeConversation}
        onUpdateConversation={updateConversation}
        sidebarOpen={state.sidebarOpen}
      />
    </div>
  );
};

export default App;
