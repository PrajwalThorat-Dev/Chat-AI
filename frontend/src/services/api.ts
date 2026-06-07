//Connect to the backend API using axios to send messages and fetch chat history.

import axios from "axios"
import type { SendMessageRequest, SendMessageResponse } from "../types/chat"

const BASE_URL = "http://127.0.0.1:8000/api"

export const sendMessage = async (
  payload: SendMessageRequest
): Promise<SendMessageResponse> => {
  const response = await axios.post<SendMessageResponse>(
    `${BASE_URL}/chat`,
    payload
  )
  return response.data
}

export const fetchHistory = async (sessionId: string) => {
  const response = await axios.get(`${BASE_URL}/history/${sessionId}`)
  return response.data
}