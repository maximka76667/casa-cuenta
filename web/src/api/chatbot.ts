// web/src/api/chatbot.ts
import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export interface ChatResponse {
  response: string;
}

export const sendChatMessage = async (
  message: string,
  groupId: string
): Promise<ChatResponse> => {
  const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat/`, {
    message,
    group_id: groupId,
  });

  return response.data;
};
