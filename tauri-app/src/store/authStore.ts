import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
    id: string;
    email: string;
    is_active: boolean;
}

interface AuthState {
    token: string | null;
    refreshToken: string | null;
    user: User | null;
    isAuthenticated: boolean;
    setAuth: (token: string, refreshToken: string, user: User) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            token: null,
            refreshToken: null,
            user: null,
            isAuthenticated: false,
            setAuth: (token, refreshToken, user) =>
                set({ token, refreshToken, user, isAuthenticated: true }),
            logout: () =>
                set({ token: null, refreshToken: null, user: null, isAuthenticated: false }),
        }),
        {
            name: 'auth-storage',
        }
    )
);
