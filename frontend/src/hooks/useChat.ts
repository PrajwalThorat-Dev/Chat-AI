//Custom React hook to manage chat state, including messages, loading status, and error handling. It provides a send function to handle user input and communicate with the backend API.
import { useState } from "react"
import type { Message } from "../types/chat"
import { sendMessage } from "../services/api"

const SESSION_ID = "session_001"   // hardcoded for now, dynamic later

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addMessage = (role: "user" | "assistant", content: string) => {
    const newMessage: Message = {
      id: crypto.randomUUID(),
      role,
      content,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, newMessage])
    return newMessage
  }

  const send = async (userInput: string) => {
    if (!userInput.trim()) return

    addMessage("user", userInput)
    setLoading(true)
    setError(null)

    try {
      const response = await sendMessage({
        session_id: SESSION_ID,
        message: userInput,
      })
      addMessage("assistant", response.reply)
    } catch (err) {
      setError("Something went wrong. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return { messages, loading, error, send }
}