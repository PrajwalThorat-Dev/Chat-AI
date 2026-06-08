// useChat.ts
// Manages chat state, PDF selection, and message sending.
// Automatically uses RAG mode when a PDF is selected.

import { useState, useEffect } from "react"
import type { Message } from "../types/chat"
import { sendMessage, uploadPdf, listPdfs, deletePdf } from "../services/api"

const SESSION_ID = "session_001"

export interface PdfItem {
  pdf_id: string
  filename: string
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // PDF state
  const [pdfs, setPdfs] = useState<PdfItem[]>([])
  const [selectedPdf, setSelectedPdf] = useState<PdfItem | null>(null)
  const [uploading, setUploading] = useState(false)

  // Load PDF list on mount
  useEffect(() => {
    loadPdfs()
  }, [])

  const loadPdfs = async () => {
    try {
      const list = await listPdfs()
      setPdfs(list)
    } catch {
      // silently fail if no PDFs yet
    }
  }

  const addMessage = (role: "user" | "assistant", content: string, mode?: "chat" | "rag") => {
    const newMessage: Message = {
      id: crypto.randomUUID(),
      role,
      content,
      timestamp: new Date(),
      mode
    }
    setMessages((prev) => [...prev, newMessage])
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
        pdf_id: selectedPdf?.pdf_id     // sends pdf_id if a PDF is selected
      })
      addMessage("assistant", response.reply, response.mode)
    } catch {
      setError("Something went wrong. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (file: File) => {
    setUploading(true)
    setError(null)
    try {
      const result = await uploadPdf(file)
      await loadPdfs()                  // refresh PDF list after upload
      // Auto select the newly uploaded PDF
      setSelectedPdf({ pdf_id: result.pdf_id, filename: result.filename })
    } catch {
      setError("Failed to upload PDF. Please try again.")
    } finally {
      setUploading(false)
    }
  }

  const handleDeletePdf = async (pdfId: string) => {
    try {
      await deletePdf(pdfId)
      if (selectedPdf?.pdf_id === pdfId) {
        setSelectedPdf(null)            // deselect if active PDF is deleted
      }
      await loadPdfs()
    } catch {
      setError("Failed to delete PDF.")
    }
  }

  return {
    messages, loading, error, send,
    pdfs, selectedPdf, setSelectedPdf,
    uploading, handleUpload, handleDeletePdf
  }
}