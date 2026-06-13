// FileReaderPanel.tsx
// Panel for uploading any file type and asking questions about it directly.
// Different from PdfPanel — no chunking, no ChromaDB, full text sent to LLaMA.

import { useRef } from "react"

interface Props {
  fileReading: boolean
  onReadFile: (file: File) => void    // ← no question parameter
}

const FileReaderPanel = ({ fileReading, onReadFile }: Props) => {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onReadFile(file)    // immediately read on select
    e.target.value = ""
  }

  return (
    <div style={{
      borderTop: "1px solid #2a2a2a",
      padding: "12px",
      display: "flex",
      flexDirection: "column",
      gap: "8px"
    }}>
      <p style={{ color: "#888", fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px" }}>
        Direct File Read
      </p>

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={fileReading}
        style={{
          padding: "8px",
          background: fileReading ? "#333" : "#1a1a1a",
          color: fileReading ? "#888" : "#ccc",
          border: "1px solid #2a2a2a",
          borderRadius: "6px",
          cursor: fileReading ? "not-allowed" : "pointer",
          fontSize: "12px"
        }}
      >
        {fileReading ? "Reading..." : "+ Add file"}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt,.csv,.docx,.json,.py,.js,.ts,.md"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
    </div>
  )
}

export default FileReaderPanel