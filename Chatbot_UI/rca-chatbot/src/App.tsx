// App.tsx - Fixed to ensure API call happens automatically
import React, { useState, useEffect } from 'react';
import ChatSidebar from './components/ChatSidebar';
import ChatWindow from './components/ChatWindow';
import JiraModal from './components/JiraModal';
import { Conversation, Message, AppState } from './types';
import './App.css';

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    conversations: [],
    activeConversationId: null,
    sidebarOpen: true,
    isLoading: false
  });
  const [modalOpen, setModalOpen] = useState(false);

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

  const handleNewAnalysisClick = (): void => {
    setModalOpen(true);
  };

  // API call function
  const callRCAAPI = async (message: string, conversationId: string, jiraId: string): Promise<string> => {
    try {
      const requestBody = {
        message,
        conversationId,
        history: [],
        metadata: {
          sessionId: `session_${Date.now()}`,
          analysisType: 'jira_investigation',
          jiraId: jiraId
        }
      };

      console.log('Calling RCA API with:', requestBody); // Debug log

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
      return data.analysis || data.response || `Started analysis for JIRA ticket ${jiraId}. Here's what I found initially...`;

    } catch (error) {
      console.error('RCA API Error:', error);
      return `I've started the analysis for JIRA ticket ${jiraId}. However, I encountered an issue connecting to the backend. Please check your API configuration and try asking a follow-up question.`;
    }
  };

  // Create conversation with JIRA ID and immediately call API
  const createConversationWithJira = async (jiraId: string): Promise<void> => {
    const conversationId = Date.now().toString();
    
    const newConversation: Conversation = {
      id: conversationId,
      title: `Analysis: ${jiraId}`,
      jiraId: jiraId,
      messages: [],
      createdAt: new Date(),
      metadata: {
        totalMessages: 0,
        status: 'active',
        analysisType: 'jira_investigation'
      }
    };

    // Add conversation to state first
    setState(prev => ({
      ...prev,
      conversations: [newConversation, ...prev.conversations],
      activeConversationId: conversationId,
      isLoading: true // Set loading state
    }));

    // Close modal
    setModalOpen(false);

    // Create the first user message
    const firstUserMessage: Message = {
      id: `msg_${Date.now()}_user`,
      content: `Investigate JIRA ticket ${jiraId}`,
      role: 'user',
      timestamp: new Date(),
      metadata: {
        processingTime: 0
      }
    };

    // Update conversation with user message
    setState(prev => ({
      ...prev,
      conversations: prev.conversations.map(conv => 
        conv.id === conversationId 
          ? { ...conv, messages: [firstUserMessage] }
          : conv
      )
    }));

    try {
      // Call the API
      const startTime = Date.now();
      console.log(`Making API call for JIRA ${jiraId}...`); // Debug log
      
      const response = await callRCAAPI(
        `Investigate JIRA ticket ${jiraId}`, 
        conversationId, 
        jiraId
      );
      
      const processingTime = Date.now() - startTime;

      // Create bot response message
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

      // Update conversation with both messages
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv => 
          conv.id === conversationId 
            ? { 
                ...conv, 
                messages: [firstUserMessage, botMessage],
                updatedAt: new Date(),
                metadata: {
                  ...conv.metadata,
                  totalMessages: 2,
                  status: 'active' as const
                }
              }
            : conv
        ),
        isLoading: false
      }));

    } catch (error) {
      console.error('Error in createConversationWithJira:', error);
      
      // Create error message
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        content: 'I encountered an error while starting the analysis. Please try asking a follow-up question or check your API configuration.',
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          processingTime: 0,
          confidence: 0
        }
      };

      // Update with error message
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv => 
          conv.id === conversationId 
            ? { 
                ...conv, 
                messages: [firstUserMessage, errorMessage],
                updatedAt: new Date(),
                metadata: {
                  ...conv.metadata,
                  totalMessages: 2,
                  status: 'active' as const
                }
              }
            : conv
        ),
        isLoading: false
      }));
    }
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
              title: conv.jiraId 
                ? `Analysis: ${conv.jiraId}` 
                : (messages.length > 0 
                    ? messages[0].content.substring(0, 50) + (messages[0].content.length > 50 ? '...' : '')
                    : 'New RCA Analysis'),
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
        onNewConversation={handleNewAnalysisClick}
        onDeleteConversation={deleteConversation}
        isOpen={state.sidebarOpen}
        onToggle={toggleSidebar}
      />
      <ChatWindow
        conversation={activeConversation}
        onUpdateConversation={updateConversation}
        sidebarOpen={state.sidebarOpen}
        isLoading={state.isLoading} // Pass loading state
      />

      {/* JIRA Modal */}
      <JiraModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={createConversationWithJira}
      />
    </div>
  );
};

export default App;
