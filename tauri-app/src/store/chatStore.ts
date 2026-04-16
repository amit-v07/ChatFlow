import { create } from 'zustand';
import { api } from '../services/api';

interface Message {
    id: string;
    conversation_id: string;
    sender_id: string;
    content: string;
    message_type: 'text' | 'image' | 'file';
    created_at: string;
}

interface Conversation {
    id: string;
    type: 'private' | 'group';
    name?: string;
    participants: {
        user: {
            id: string;
            email: string;
        }
    }[];
    last_message?: Message;
}

interface ChatState {
    conversations: Conversation[];
    activeConversation: Conversation | null;
    messages: Record<string, Message[]>; // conversation_id -> messages
    isLoading: boolean;
    error: string | null;

    fetchConversations: (token: string) => Promise<void>;
    setActiveConversation: (conversation: Conversation) => void;
    addMessage: (message: Message) => void;
    startChatWithFriend: (friendId: string, token: string) => Promise<void>; // Find or create conversation
}

export const useChatStore = create<ChatState>((set, get) => ({
    conversations: [],
    activeConversation: null,
    messages: {},
    isLoading: false,
    error: null,

    fetchConversations: async (token) => {
        set({ isLoading: true });
        try {
            const conversations = await api.getConversations(token);
            set({ conversations, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    setActiveConversation: (conversation) => {
        set({ activeConversation: conversation });
        // Optionally fetch history here if not loaded
    },

    addMessage: (message) => {
        set((state) => {
            const conversationMessages = state.messages[message.conversation_id] || [];
            return {
                messages: {
                    ...state.messages,
                    [message.conversation_id]: [...conversationMessages, message]
                }
            };
        });
    },

    startChatWithFriend: async (friendId, token) => {
        // 1. Check if we already have a conversation with this friend
        const { conversations } = get();
        const existing = conversations.find(c =>
            c.type === 'private' &&
            c.participants.some(p => p.user.id === friendId)
        );

        if (existing) {
            set({ activeConversation: existing });
            return;
        }

        // 2. If not, create/get one from backend
        try {
            const conversation = await api.createPrivateChat(friendId, token);

            // Update conversations list
            set((state) => ({
                conversations: [conversation, ...state.conversations],
                activeConversation: conversation
            }));
        } catch (err: any) {
            set({ error: err.message });
        }
    }
}));
