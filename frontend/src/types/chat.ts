export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  mode?: "chat" | "rag"             // optional — shows which mode was used
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