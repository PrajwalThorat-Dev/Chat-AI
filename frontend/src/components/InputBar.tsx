import { useState } from "react"

interface Props {
  onSend: (message: string) => void
  loading: boolean
}

const InputBar = ({ onSend, loading }: Props) => {
  const [input, setInput] = useState("")

  const handleSend = () => {
    if (!input.trim()) return
    onSend(input)
    setInput("")
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{
      display: "flex",
      padding: "12px 20px",
      borderTop: "1px solid #333",
      gap: "10px",
    }}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message..."
        disabled={loading}
        style={{
          flex: 1,
          padding: "10px 14px",
          borderRadius: "8px",
          border: "1px solid #444",
          background: "#1e1e1e",
          color: "#fff",
          fontSize: "14px",
        }}
      />
      <button
        onClick={handleSend}
        disabled={loading}
        style={{
          padding: "10px 20px",
          borderRadius: "8px",
          background: loading ? "#555" : "#0078d4",
          color: "#fff",
          border: "none",
          cursor: loading ? "not-allowed" : "pointer",
          fontSize: "14px",
        }}
      >
        {loading ? "..." : "Send"}
      </button>
    </div>
  )
}

export default InputBar