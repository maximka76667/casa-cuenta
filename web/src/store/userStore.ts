import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
}

interface UserState {
  user: User | null;
  accessToken: string;
  setUser: (user: User | null) => void;
  setAccessToken: (accessToken: string) => void;
  clearUser: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: "",
      setUser: (user) => set({ user }),
      setAccessToken: (accessToken) => set({ accessToken }),
      clearUser: () => set({ user: null }),
    }),
    {
      name: "user-storage", // key in localStorage
    }
  )
);

// export const useUserStore = create<UserState>((set) => ({
//   user: null,
//   accessToken: "",
//   setUser: (user) => set({ user }),
//   setAccessToken: (accessToken) => set({ accessToken }),
//   clearUser: () => set({ user: null }),
// }));
