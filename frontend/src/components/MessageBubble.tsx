import ReactMarkdown from "react-markdown"
import type { Message } from "../types/chat"

interface Props {
  message: Message
}

const MessageBubble = ({ message }: Props) => {
  const isUser = message.role === "user"

  return (
    <div style={{
      display: "flex",
      justifyContent: isUser ? "flex-end" : "flex-start",
      marginBottom: "10px"
    }}>
      <div style={{
        background: isUser ? "#0078d4" : "#2a2a2a",
        color: "#fff",
        padding: "10px 14px",
        borderRadius: "12px",
        maxWidth: "70%",
        fontSize: "14px",
        lineHeight: "1.6"
      }}>
        {isUser ? (
          message.content
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </div>
    </div>
  )
}

export default MessageBubble