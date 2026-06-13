export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  mode?: "chat" | "rag"  | "direct_read"           
}

export interface SendMessageRequest {
  session_id: string
  message: string
  pdf_id?: string                   // optional — triggers RAG when present
}

export interface SendMessageResponse {
  reply: string
  session_id: string
  mode: "chat" | "rag"
}

export interface DirectFileResponse {
  filename: string
  question: string
  answer: string
  mode: "direct_read"
}