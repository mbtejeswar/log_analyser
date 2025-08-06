// components/JiraModal.tsx - Updated with modern styling
import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface JiraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (jiraId: string) => void;
}

const JiraModal: React.FC<JiraModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [jiraId, setJiraId] = useState('');

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!jiraId.trim()) return;
    onSubmit(jiraId.trim());
    setJiraId('');
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal">
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          <X size={20} />
        </button>
        
        <h3>Start New RCA Analysis</h3>
        
        <form onSubmit={handleSubmit}>
          <label htmlFor="jira-input">JIRA Ticket ID</label>
          <input
            id="jira-input"
            type="text"
            placeholder="e.g., RCA-1234, INCIDENT-5678"
            value={jiraId}
            onChange={(e) => setJiraId(e.target.value)}
            autoFocus
            required
          />
          
          <button 
            type="submit" 
            className="modal-submit"
            disabled={!jiraId.trim()}
          >
            Continue Analysis
          </button>
        </form>
      </div>
    </div>
  );
};

export default JiraModal;
