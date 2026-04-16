import { create } from 'zustand';
import { api } from '../services/api';

interface User {
    id: string;
    email: string;
    is_active: boolean;
}

interface FriendRequest {
    id: string;
    sender: User;
    receiver: User;
    status: string;
    created_at: string;
}

interface Friend {
    id: string;
    friend: User;
    created_at: string;
}

interface FriendState {
    friends: Friend[];
    pendingRequests: FriendRequest[];
    searchResults: User[];
    isLoading: boolean;
    error: string | null;

    searchUsers: (query: string, token: string) => Promise<void>;
    sendFriendRequest: (receiverId: string, token: string) => Promise<void>;
    fetchPendingRequests: (token: string) => Promise<void>;
    fetchFriends: (token: string) => Promise<void>;
    respondToRequest: (requestId: string, status: 'accepted' | 'rejected', token: string) => Promise<void>;
    clearSearch: () => void;
    addIncomingRequest: (request: FriendRequest) => void;
}

export const useFriendStore = create<FriendState>((set, get) => ({
    friends: [],
    pendingRequests: [],
    searchResults: [],
    isLoading: false,
    error: null,

    searchUsers: async (query, token) => {
        set({ isLoading: true, error: null });
        try {
            const results = await api.searchUsers(query, token);
            set({ searchResults: results, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    sendFriendRequest: async (receiverId, token) => {
        set({ isLoading: true });
        try {
            await api.sendFriendRequest(receiverId, token);
            set({ isLoading: false });
            // clear search or show success?
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
            throw err;
        }
    },

    fetchPendingRequests: async (token) => {
        try {
            const requests = await api.getPendingRequests(token);
            set({ pendingRequests: requests });
        } catch (err: any) {
            console.error(err);
        }
    },

    fetchFriends: async (token) => {
        try {
            const friends = await api.getFriends(token);
            set({ friends: friends });
        } catch (err: any) {
            console.error(err);
        }
    },

    respondToRequest: async (requestId, status, token) => {
        try {
            await api.respondToFriendRequest(requestId, status, token);
            // Remove from pending
            set((state) => ({
                pendingRequests: state.pendingRequests.filter((r) => r.id !== requestId),
            }));
            // If accepted, refresh friends list
            if (status === 'accepted') {
                get().fetchFriends(token);
            }
        } catch (err: any) {
            set({ error: err.message });
        }
    },

    clearSearch: () => set({ searchResults: [] }),

    addIncomingRequest: (request: FriendRequest) => {
        set((state) => ({
            pendingRequests: [request, ...state.pendingRequests]
        }));
    }
}));
