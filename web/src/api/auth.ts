import axios from "axios";
import { useUserStore } from "../store/userStore";

const API_BASE_URL = "http://localhost:8000"; // change to your FastAPI URL

export const signin = async (email: string, password: string) => {
  const res = await axios.post(
    `${API_BASE_URL}/signin`,
    {
      email,
      password,
    },
    {
      withCredentials: true, // if your backend uses cookies
    }
  );

  // Save user globally
  useUserStore.getState().setUser(res.data.user);
  useUserStore.getState().setAccessToken(res.data.accessToken);

  return res.data;
};

export const signup = async (email: string, password: string) => {
  const res = await axios.post(
    `${API_BASE_URL}/signup`,
    {
      email,
      password,
    },
    {
      withCredentials: true,
    }
  );
  return res.data;
};
