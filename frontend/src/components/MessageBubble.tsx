import React from 'react';
import { Message } from '../types/chat';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  return (
    <div className={`message-bubble ${message.role}`}>
      <p>{message.content}</p>
    </div>
  );
};

export default MessageBubble;
