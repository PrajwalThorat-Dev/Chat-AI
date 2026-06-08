// api.ts
// All HTTP calls to the backend API.
// Handles chat, history, PDF upload, listing, and deletion.

import axios from "axios"
import type { SendMessageRequest, SendMessageResponse } from "../types/chat"

const BASE_URL = "http://127.0.0.1:8000/api"

// Send a chat message (normal or RAG mode based on pdf_id)
export const sendMessage = async (
  payload: SendMessageRequest
): Promise<SendMessageResponse> => {
  const response = await axios.post<SendMessageResponse>(
    `${BASE_URL}/chat`,
    payload
  )
  return response.data
}

// Fetch chat history for a session
export const fetchHistory = async (sessionId: string) => {
  const response = await axios.get(`${BASE_URL}/history/${sessionId}`)
  return response.data
}

// Upload a PDF file
export const uploadPdf = async (file: File): Promise<{ pdf_id: string; filename: string }> => {
  const formData = new FormData()
  formData.append("file", file)
  const response = await axios.post(`${BASE_URL}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" }
  })
  return response.data
}

// Get list of all uploaded PDFs
export const listPdfs = async (): Promise<{ pdf_id: string; filename: string }[]> => {
  const response = await axios.get(`${BASE_URL}/pdfs`)
  return response.data.pdfs
}

// Delete a PDF by id
export const deletePdf = async (pdfId: string): Promise<void> => {
  await axios.delete(`${BASE_URL}/pdfs/${pdfId}`)
}