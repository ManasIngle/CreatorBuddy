import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, Channel } from "@/types";

interface AppState {
  user: User | null;
  activeChannel: Channel | null;
  accessToken: string | null;
  setUser: (user: User | null) => void;
  setActiveChannel: (channel: Channel | null) => void;
  setAccessToken: (token: string | null) => void;
  logout: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      activeChannel: null,
      accessToken: null,
      setUser: (user) => set({ user }),
      setActiveChannel: (channel) => set({ activeChannel: channel }),
      setAccessToken: (token) => {
        if (token) localStorage.setItem("access_token", token);
        else localStorage.removeItem("access_token");
        set({ accessToken: token });
      },
      logout: () => {
        localStorage.removeItem("access_token");
        set({ user: null, activeChannel: null, accessToken: null });
      },
    }),
    { name: "creatoriq-store", partialize: (state) => ({ user: state.user, activeChannel: state.activeChannel }) }
  )
);