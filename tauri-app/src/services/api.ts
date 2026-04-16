export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000';

export const api = {
    login: async (email: string, password: string) => {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        if (!response.ok) throw new Error('Login failed');
        return response.json();
    },

    register: async (email: string, password: string) => {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        if (!response.ok) throw new Error('Registration failed');
        return response.json();
    },

    // Friend System
    searchUsers: async (query: string, token: string) => {
        const response = await fetch(`${API_URL}/api/friends/search?query=${query}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Search failed');
        return response.json();
    },

    sendFriendRequest: async (receiverId: string, token: string) => {
        const response = await fetch(`${API_URL}/api/friends/request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ receiver_id: receiverId }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send request');
        }
        return response.json();
    },

    getPendingRequests: async (token: string) => {
        const response = await fetch(`${API_URL}/api/friends/requests`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Failed to fetch requests');
        return response.json();
    },

    getFriends: async (token: string) => {
        const response = await fetch(`${API_URL}/api/friends`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Failed to fetch friends');
        return response.json();
    },

    respondToFriendRequest: async (requestId: string, status: 'accepted' | 'rejected', token: string) => {
        const response = await fetch(`${API_URL}/api/friends/request/${requestId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status }),
        });
        if (!response.ok) throw new Error('Failed to respond to request');
        return response.json();
    },

    // Chat System
    getConversations: async (token: string) => {
        const response = await fetch(`${API_URL}/api/chat/conversations`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch conversations');
        return response.json();
    },

    createPrivateChat: async (friendId: string, token: string) => {
        const response = await fetch(`${API_URL}/api/chat/private`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ friend_id: friendId }),
        });
        if (!response.ok) throw new Error('Failed to create private chat');
        return response.json();
    },
};
