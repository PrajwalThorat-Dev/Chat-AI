import ChatWindow from "./components/ChatWindow"
import InputBar from "./components/InputBar"
import { useChat } from "./hooks/useChat"

function App() {
  const { messages, loading, error, send } = useChat()

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "100vh",
      background: "#121212",
      color: "#fff",
      fontFamily: "sans-serif",
    }}>
      <div style={{
        padding: "16px 20px",
        borderBottom: "1px solid #333",
        fontSize: "18px",
        fontWeight: 600,
      }}>
        Chat-AI
      </div>

      <ChatWindow messages={messages} />

      {error && (
        <p style={{ color: "red", textAlign: "center", margin: "4px 0" }}>
          {error}
        </p>
      )}

      <InputBar onSend={send} loading={loading} />
    </div>
  )
}

export default App