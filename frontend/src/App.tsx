// App.tsx
// Root component. Connects PdfPanel, ChatWindow, and InputBar.
// Passes PDF state down from useChat hook to all components.

import ChatWindow from "./components/ChatWindow"
import InputBar from "./components/InputBar"
import PdfPanel from "./components/PdfPanel"
import { useChat } from "./hooks/useChat"

function App() {
  const {
    messages, loading, error, send,
    pdfs, selectedPdf, setSelectedPdf,
    uploading, handleUpload, handleDeletePdf
  } = useChat()

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "100vh",
      background: "#121212",
      color: "#fff",
      fontFamily: "sans-serif",
    }}>
      {/* Header */}
      <div style={{
        padding: "16px 20px",
        borderBottom: "1px solid #2a2a2a",
        fontSize: "18px",
        fontWeight: 600,
        display: "flex",
        alignItems: "center",
        gap: "10px"
      }}>
        Chat-AI
        {selectedPdf && (
          <span style={{ fontSize: "12px", color: "#4caf50", fontWeight: 400 }}>
            — RAG mode ({selectedPdf.filename})
          </span>
        )}
      </div>

      {/* Main content: sidebar + chat */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <PdfPanel
          pdfs={pdfs}
          selectedPdf={selectedPdf}
          uploading={uploading}
          onUpload={handleUpload}
          onSelect={setSelectedPdf}
          onDelete={handleDeletePdf}
        />

        <div style={{ display: "flex", flexDirection: "column", flex: 1, overflow: "hidden" }}>
          <ChatWindow messages={messages} />

          {error && (
            <p style={{ color: "red", textAlign: "center", margin: "4px 0", fontSize: "13px" }}>
              {error}
            </p>
          )}

          <InputBar onSend={send} loading={loading} />
        </div>
      </div>
    </div>
  )
}

export default App