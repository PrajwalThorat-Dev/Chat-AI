//Define TypeScript interfaces for chat messages, chat sessions, and API request/response structures to ensure type safety when interacting with the backend API.

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export interface ChatSession {
  sessionId: string
  messages: Message[]
}

export interface SendMessageRequest {
  session_id: string
  message: string
}

export interface SendMessageResponse {
  reply: string
  session_id: string
}