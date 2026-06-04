import { Message } from '../types/chat';

export const sendMessage = async (text: string): Promise<Message> => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  const data = await response.json();

  return {
    id: data.id || `${Date.now()}-assistant`,
    role: 'assistant',
    content: data.content || '',
  };
};
