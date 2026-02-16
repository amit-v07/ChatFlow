import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';

export const useWebSocket = (url: string) => {
    const [isConnected, setIsConnected] = useState(false);
    const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
    const [lastMessage, setLastMessage] = useState<any>(null);
    const ws = useRef<WebSocket | null>(null);
    const { token } = useAuthStore();

    useEffect(() => {
        if (!token) return;

        // Ensure we don't create multiple connections
        if (ws.current?.readyState === WebSocket.OPEN) return;

        const socket = new WebSocket(`${url}?token=${token}`);

        socket.onopen = () => {
            setIsConnected(true);
            console.log('WebSocket connected');
            // Request online users on connect
            socket.send(JSON.stringify({ type: 'get_online_users' }));
        };

        socket.onclose = () => {
            setIsConnected(false);
            ws.current = null;
            console.log('WebSocket disconnected');
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // Handle presence updates internally
                if (data.type === 'presence_update') {
                    setOnlineUsers(prev => {
                        if (data.status === 'online') {
                            return [...new Set([...prev, data.user_id])];
                        } else {
                            return prev.filter(id => id !== data.user_id);
                        }
                    });
                } else if (data.type === 'online_users') {
                    setOnlineUsers(data.users);
                }

                setLastMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        ws.current = socket;

        return () => {
            if (ws.current) {
                ws.current.close();
                ws.current = null;
            }
        };
    }, [url, token]);

    const sendMessage = useCallback((message: any) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket is not connected');
        }
    }, []);

    return { isConnected, lastMessage, sendMessage, onlineUsers };
};
