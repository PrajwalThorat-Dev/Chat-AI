import { useEffect, useRef } from "react"
import type { Message } from "../types/chat"
import MessageBubble from "./MessageBubble"

interface Props {
  messages: Message[]
}

const ChatWindow = ({ messages }: Props) => {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div style={{
      flex: 1,
      overflowY: "auto",
      padding: "20px",
      display: "flex",
      flexDirection: "column",
    }}>
      {messages.length === 0 && (
        <p style={{ color: "#888", textAlign: "center", marginTop: "40px" }}>
          Send a message to start chatting
        </p>
      )}
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}

export default ChatWindow