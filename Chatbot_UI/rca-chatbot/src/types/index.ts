// types/index.ts - Complete type definitions for the chatbot

export interface Message {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: Date;
    metadata?: {
      tokens?: number;
      model?: string;
      processingTime?: number;
      confidence?: number;
    };
  }
  
  export interface Conversation {
    id: string;
    title: string;
    jiraId?: string; 
    messages: Message[];
    createdAt: Date;
    updatedAt?: Date;
    metadata?: {
      totalMessages?: number;
      analysisType?: string;
      status?: 'active' | 'resolved' | 'pending';
      tags?: string[];
    };
  }
  
  export interface ChatSidebarProps {
    conversations: Conversation[];
    activeConversationId: string | null;
    onSelectConversation: (id: string) => void;
    onNewConversation: () => void;
    onDeleteConversation: (id: string) => void;
    isOpen: boolean;
    onToggle: () => void;
  }
  
  export interface ChatWindowProps {
    conversation: Conversation | undefined;
    onUpdateConversation: (id: string, messages: Message[]) => void;
    sidebarOpen: boolean;
  }
  
  // API Response types for your RCA backend
  export interface RCAApiRequest {
    message: string;
    conversationId: string;
    history: Array<{
      role: 'user' | 'assistant';
      content: string;
    }>;
    metadata?: {
      sessionId?: string;
      userId?: string;
      analysisType?: string;
    };
  }
  
  export interface RCAApiResponse {
    analysis: string;
    response: string;
    conversationId: string;
    timestamp: string;
    metadata?: {
      confidence?: number;
      processingTime?: number;
      model?: string;
      tokens?: number;
      suggestions?: string[];
    };
  }
  
  // App state types
  export interface AppState {
    conversations: Conversation[];
    activeConversationId: string | null;
    sidebarOpen: boolean;
    isLoading: boolean;
    error?: string;
  }
  