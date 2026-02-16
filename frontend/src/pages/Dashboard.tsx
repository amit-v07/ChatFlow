import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { useFriendStore } from '../store/friendStore';
import { useChatStore } from '../store/chatStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { WS_URL } from '../services/api';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { FriendRequests } from '../components/friends/FriendRequests';

export const Dashboard = () => {
    const { token } = useAuthStore();
    const { fetchFriends } = useFriendStore();
    const { activeConversation, startChatWithFriend, addMessage, messages } = useChatStore();
    const [inputMessage, setInputMessage] = useState('');

    // Connect to Main WebSocket for presence and notifications
    const { isConnected, lastMessage, onlineUsers } = useWebSocket(`${WS_URL}/ws`);

    // Connect to Chat WebSocket
    const {
        sendMessage: sendChatMessage,
        lastMessage: lastChatMessage,
        isConnected: isChatConnected
    } = useWebSocket(`${WS_URL}/ws/chat`);

    useEffect(() => {
        if (lastMessage) {
            if (lastMessage.type === 'friend_request_received') {
                useFriendStore.getState().fetchPendingRequests(token!);
                alert(`New friend request!`);
            } else if (lastMessage.type === 'friend_request_accepted') {
                alert(`Friend request accepted!`);
                fetchFriends(token!);
            }
        }
    }, [lastMessage, fetchFriends, token]);

    useEffect(() => {
        if (lastChatMessage) {
            if (lastChatMessage.type === 'new_message' || lastChatMessage.type === 'message_sent') {
                addMessage(lastChatMessage.message); // Ensure payload matches backend
            }
        }
    }, [lastChatMessage, addMessage]);

    const handleSelectFriend = (friendId: string) => {
        console.log('Dashboard handleSelectFriend called with:', friendId);
        if (token) {
            startChatWithFriend(friendId, token);
        }
    };

    const handleSend = () => {
        if (!inputMessage.trim() || !activeConversation) return;

        sendChatMessage({
            type: 'send_message',
            conversation_id: activeConversation.id,
            content: inputMessage,
            message_type: 'text'
        });
        setInputMessage('');
    };

    const currentMessages = activeConversation ? (messages[activeConversation.id] || []) : [];

    return (
        <DashboardLayout onlineUsers={onlineUsers} onSelectFriend={handleSelectFriend}>
            <div className="flex flex-col h-full">
                <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-gray-800">
                        {activeConversation ? 'Chat' : 'Dashboard'}
                    </h2>
                    <div className="flex items-center gap-2">
                        <span className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} title={`Notifications: ${isConnected ? "Connected" : "Disconnected"}`}></span>
                        <span className={`w-3 h-3 rounded-full ${isChatConnected ? 'bg-blue-500' : 'bg-orange-500'}`} title={`Chat: ${isChatConnected ? "Connected" : "Disconnected"}`}></span>
                    </div>
                </header>

                <div className="flex-1 flex flex-col overflow-hidden">
                    {!activeConversation && (
                        <div className="p-6">
                            <FriendRequests />
                            <div className="mt-8 text-center text-gray-500">
                                <p className="text-lg">Select a friend to start chatting</p>
                            </div>
                        </div>
                    )}

                    {activeConversation && (
                        <div className="flex flex-col h-full bg-gray-50">
                            {/* Messages Area */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                                {currentMessages.map((msg, i) => (
                                    <div key={i} className={`flex ${msg.sender_id === useAuthStore.getState().user?.id ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[70%] rounded-lg px-4 py-2 ${msg.sender_id === useAuthStore.getState().user?.id
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-white border text-gray-800'
                                            }`}>
                                            <p>{msg.content}</p>
                                            <span className="text-xs opacity-70 mt-1 block">
                                                {new Date(msg.created_at).toLocaleTimeString()}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Input Area */}
                            <div className="bg-white border-t p-4">
                                <form
                                    onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                                    className="flex gap-2"
                                >
                                    <input
                                        type="text"
                                        value={inputMessage}
                                        onChange={(e) => setInputMessage(e.target.value)}
                                        className="flex-1 rounded-full border border-gray-300 px-4 py-2 focus:outline-none focus:border-blue-500"
                                        placeholder="Type a message..."
                                    />
                                    <button
                                        type="submit"
                                        disabled={!inputMessage.trim()}
                                        className="bg-blue-600 text-white rounded-full p-2 hover:bg-blue-700 disabled:opacity-50"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                                        </svg>
                                    </button>
                                </form>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
};
