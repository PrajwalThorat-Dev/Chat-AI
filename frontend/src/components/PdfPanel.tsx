// PdfPanel.tsx
// Sidebar panel for uploading PDFs, selecting active PDF, and deleting old ones.
// When a PDF is selected, chat automatically switches to RAG mode.

import { useRef } from "react"
import type { PdfItem } from "../hooks/useChat"

interface Props {
  pdfs: PdfItem[]
  selectedPdf: PdfItem | null
  uploading: boolean
  onUpload: (file: File) => void
  onSelect: (pdf: PdfItem | null) => void
  onDelete: (pdfId: string) => void
}

const PdfPanel = ({ pdfs, selectedPdf, uploading, onUpload, onSelect, onDelete }: Props) => {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onUpload(file)
    // reset input so same file can be re-uploaded
    e.target.value = ""
  }

  return (
    <div style={{
      width: "240px",
      borderRight: "1px solid #2a2a2a",
      display: "flex",
      flexDirection: "column",
      padding: "16px 12px",
      gap: "12px",
      background: "#0f0f0f"
    }}>
      <p style={{ color: "#888", fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px" }}>
        PDF Documents
      </p>

      {/* Upload button */}
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        style={{
          padding: "8px",
          background: uploading ? "#333" : "#0078d4",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: uploading ? "not-allowed" : "pointer",
          fontSize: "13px"
        }}
      >
        {uploading ? "Uploading..." : "+ Upload PDF"}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      {/* PDF list */}
      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
        {pdfs.length === 0 && (
          <p style={{ color: "#555", fontSize: "12px" }}>No PDFs uploaded yet</p>
        )}

        {pdfs.map((pdf) => {
          const isSelected = selectedPdf?.pdf_id === pdf.pdf_id
          return (
            <div
              key={pdf.pdf_id}
              style={{
                background: isSelected ? "#1a3a5c" : "#1a1a1a",
                border: isSelected ? "1px solid #0078d4" : "1px solid #2a2a2a",
                borderRadius: "6px",
                padding: "8px",
                cursor: "pointer",
              }}
              onClick={() => onSelect(isSelected ? null : pdf)}  // toggle selection
            >
              <p style={{
                color: isSelected ? "#60aaff" : "#ccc",
                fontSize: "12px",
                marginBottom: "4px",
                wordBreak: "break-word"
              }}>
                {pdf.filename}
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation()                             // prevent selecting while deleting
                  onDelete(pdf.pdf_id)
                }}
                style={{
                  background: "transparent",
                  color: "#ff4444",
                  border: "none",
                  cursor: "pointer",
                  fontSize: "11px",
                  padding: 0
                }}
              >
                Delete
              </button>
            </div>
          )
        })}
      </div>

      {/* Mode indicator */}
      {selectedPdf && (
        <div style={{
          marginTop: "auto",
          padding: "8px",
          background: "#0d2a0d",
          border: "1px solid #1a5c1a",
          borderRadius: "6px"
        }}>
          <p style={{ color: "#4caf50", fontSize: "11px" }}>RAG mode active</p>
          <p style={{ color: "#555", fontSize: "10px", marginTop: "2px" }}>
            Answering from selected PDF
          </p>
        </div>
      )}
    </div>
  )
}

export default PdfPanel