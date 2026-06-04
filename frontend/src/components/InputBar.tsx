import React, { useState } from 'react';

interface InputBarProps {
  onSend: (text: string) => void;
}

const InputBar: React.FC<InputBarProps> = ({ onSend }) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (!text.trim()) {
      return;
    }
    onSend(text.trim());
    setText('');
  };

  return (
    <div className="input-bar">
      <input
        type="text"
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Type your message..."
      />
      <button type="button" onClick={handleSend}>
        Send
      </button>
    </div>
  );
};

export default InputBar;
