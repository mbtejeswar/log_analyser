// utils/rcaApi.ts - RCA Backend API integration
export const callRCAAgent = async (message: string, history: any[] = []) => {
    try {
      const response = await fetch(process.env.REACT_APP_RCA_BACKEND_URL + '/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.REACT_APP_RCA_API_KEY}`
        },
        body: JSON.stringify({
          query: message,
          context: history,
          sessionId: generateSessionId()
        })
      });
  
      if (!response.ok) {
        throw new Error(`RCA Backend Error: ${response.status}`);
      }
  
      const data = await response.json();
      return data.analysis || data.response || data.message;
      
    } catch (error) {
      console.error('RCA Agent Error:', error);
      return "I'm sorry, I encountered an error while analyzing your request. Please try again.";
    }
  };
  
  const generateSessionId = () => {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
  };
  