import { useState } from 'react';
import { Message } from '../types/chat';
import { sendMessage } from '../services/api';

const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const addMessage = (message: Message) => {
    setMessages((current) => [...current, message]);
  };

  const sendUserMessage = async (content: string) => {
    const userMessage: Message = {
      id: `${Date.now()}-user`,
      role: 'user',
      content,
    };

    addMessage(userMessage);
    setLoading(true);

    try {
      const assistantMessage = await sendMessage(content);
      addMessage(assistantMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    loading,
    sendUserMessage,
  };
};

export default useChat;
