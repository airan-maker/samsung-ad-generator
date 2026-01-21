import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";
import { api } from "@/lib/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  setUser: (user: User | null) => void;
  login: (user: User) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      setUser: (user) =>
        set({
          user,
          isAuthenticated: !!user,
        }),

      login: (user) =>
        set({
          user,
          isAuthenticated: true,
        }),

      logout: async () => {
        try {
          await api.logout();
        } catch (error) {
          console.error("Logout error:", error);
        } finally {
          set({
            user: null,
            isAuthenticated: false,
          });
          // Clear localStorage
          if (typeof window !== "undefined") {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
          }
        }
      },

      refreshUser: async () => {
        set({ isLoading: true });
        try {
          const user = await api.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },
    }),
    {
      name: "saiad-auth",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Hook for checking auth status
export function useAuth() {
  const { user, isAuthenticated, isLoading, logout, refreshUser } = useAuthStore();

  return {
    user,
    isAuthenticated,
    isLoading,
    logout,
    refreshUser,
  };
}

// Hook for requiring auth
export function useRequireAuth(redirectTo: string = "/login") {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (typeof window !== "undefined" && !isLoading && !isAuthenticated) {
    window.location.href = `${redirectTo}?callbackUrl=${encodeURIComponent(window.location.pathname)}`;
  }

  return { isAuthenticated, isLoading };
}
